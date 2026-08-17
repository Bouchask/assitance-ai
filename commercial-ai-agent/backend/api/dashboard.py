from flask import Blueprint, request, jsonify
from backend.api.auth import jwt_required, roles_required
from backend.database.connection import SessionLocal
from backend.models.client import Client
from backend.models.service import Service
from backend.models.quote import Quote, QuoteItem
from backend.models.invoice import Invoice, InvoiceItem

bp = Blueprint('dashboard', __name__, url_prefix='/api')


@bp.route('/clients', methods=['GET'])
@jwt_required
def list_clients():
    db = SessionLocal()
    try:
        limit = int(request.args.get('limit', 20))
        offset = int(request.args.get('offset', 0))
        query = db.query(Client).order_by(Client.created_at.desc()).limit(limit).offset(offset).all()
        results = [
            {"id": c.id, "name": c.name, "email": c.email, "phone": c.phone, "address": c.address}
            for c in query
        ]
        return jsonify(results)
    finally:
        db.close()


@bp.route('/clients', methods=['POST'])
@jwt_required
@roles_required('ADMIN','SALES')
def create_client():
    payload = request.json or {}
    if 'name' not in payload:
        return jsonify({"error": "Missing 'name'"}), 400
    db = SessionLocal()
    try:
        client = Client(name=payload.get('name'), email=payload.get('email'), phone=payload.get('phone'), address=payload.get('address'))
        db.add(client)
        db.commit()
        db.refresh(client)
        return jsonify({"id": client.id, "name": client.name}), 201
    finally:
        db.close()


@bp.route('/services', methods=['GET'])
def list_services():
    db = SessionLocal()
    try:
        services = db.query(Service).order_by(Service.name).all()
        return jsonify([
            {"id": s.id, "code": s.code, "name": s.name, "unit_price": s.unit_price, "currency": s.currency}
            for s in services
        ])
    finally:
        db.close()


@bp.route('/services', methods=['POST'])
@jwt_required
@roles_required('ADMIN','SALES')
def create_service():
    payload = request.json or {}
    # Accept either {code,name,unit_price} or {title,price}
    if 'code' in payload and 'name' in payload and 'unit_price' in payload:
        code = payload['code']
        name = payload['name']
        unit_price = float(payload['unit_price'])
    elif 'title' in payload and 'price' in payload:
        code = payload.get('code') or payload['title'].lower().replace(' ', '-')[:20]
        name = payload['title']
        unit_price = float(payload['price'])
    else:
        return jsonify({"error": "Missing service fields (expected code,name,unit_price or title,price)"}), 400

    db = SessionLocal()
    try:
        service = Service(code=code, name=name, description=payload.get('description'), unit_price=unit_price, currency=payload.get('currency', 'MAD'))
        db.add(service)
        db.commit()
        db.refresh(service)
        return jsonify({"id": service.id, "code": service.code, "name": service.name, "price": service.unit_price}), 201
    finally:
        db.close()


@bp.route('/quotes', methods=['GET'])
@jwt_required
def list_quotes():
    db = SessionLocal()
    try:
        limit = int(request.args.get('limit', 20))
        offset = int(request.args.get('offset', 0))
        q = db.query(Quote).order_by(Quote.created_at.desc()).limit(limit).offset(offset).all()
        out = []
        for quote in q:
            out.append({
                "id": quote.id,
                "quote_number": quote.quote_number,
                "client_id": quote.client_id,
                "status": quote.status,
                "subtotal": quote.subtotal,
                "tax_total": quote.tax_total,
                "total_amount": quote.total_amount,
                "created_at": quote.created_at.isoformat() if quote.created_at else None
            })
        return jsonify(out)
    finally:
        db.close()


@bp.route('/quotes', methods=['POST'])
@jwt_required
@roles_required('ADMIN','SALES')
def create_quote():
    payload = request.json or {}
    # allow client to omit quote_number; generate server-side when missing
    required = ['client_id', 'items']
    for r in required:
        if r not in payload:
            return jsonify({"error": f"Missing '{r}'"}), 400

    import time
    quote_number = payload.get('quote_number') or f"Q-{int(time.time())}"

    db = SessionLocal()
    try:
        quote = Quote(quote_number=quote_number, client_id=int(payload['client_id']), status=payload.get('status', 'DRAFT'))
        db.add(quote)
        db.flush()

        subtotal = 0.0
        tax_total = 0.0
        for item in payload['items']:
            service_id = int(item['service_id'])
            quantity = float(item.get('quantity', 1))
            unit_price = float(item.get('unit_price'))
            tax_rate = float(item.get('tax_rate', 20.0))
            qi = QuoteItem(quote_id=quote.id, service_id=service_id, quantity=quantity, unit_price=unit_price, tax_rate=tax_rate)
            db.add(qi)
            line_ht = quantity * unit_price
            line_tax = line_ht * (tax_rate / 100.0)
            subtotal += line_ht
            tax_total += line_tax

        quote.subtotal = subtotal
        quote.tax_total = tax_total
        quote.total_amount = subtotal + tax_total
        db.commit()
        db.refresh(quote)
        return jsonify({"id": quote.id, "quote_number": quote.quote_number}), 201
    finally:
        db.close()


@bp.route('/invoices', methods=['GET'])
@jwt_required
def list_invoices():
    db = SessionLocal()
    try:
        invoices = db.query(Invoice).order_by(Invoice.created_at.desc()).limit(50).all()
        return jsonify([
            {"id": inv.id, "invoice_number": inv.invoice_number, "client_id": inv.client_id, "total_amount": inv.total_amount, "status": inv.status}
            for inv in invoices
        ])
    finally:
        db.close()


@bp.route('/invoices', methods=['POST'])
@jwt_required
@roles_required('ADMIN','SALES')
def create_invoice():
    payload = request.json or {}
    db = SessionLocal()
    try:
        # Support creating invoice from an existing quote by providing quote_id
        if 'quote_id' in payload:
            quote_id = int(payload['quote_id'])
            quote = db.query(Quote).filter(Quote.id == quote_id).first()
            if not quote:
                return jsonify({"error": "Quote not found"}), 404
            import time
            invoice_number = payload.get('invoice_number') or f"I-{int(time.time())}"
            invoice = Invoice(invoice_number=invoice_number, client_id=quote.client_id, status=payload.get('status', 'DRAFT'))
            db.add(invoice)
            db.flush()
            # copy items from quote
            items = db.query(QuoteItem).filter(QuoteItem.quote_id == quote.id).all()
            subtotal = 0.0
            tax_total = 0.0
            for it in items:
                ii = InvoiceItem(invoice_id=invoice.id, service_id=it.service_id, quantity=it.quantity, unit_price=it.unit_price, tax_rate=it.tax_rate)
                db.add(ii)
                line_ht = it.quantity * it.unit_price
                line_tax = line_ht * (it.tax_rate / 100.0)
                subtotal += line_ht
                tax_total += line_tax
            invoice.subtotal = subtotal
            invoice.tax_total = tax_total
            invoice.total_amount = subtotal + tax_total
            db.commit()
            db.refresh(invoice)
            return jsonify({"id": invoice.id, "invoice_number": invoice.invoice_number}), 201

        # Otherwise expect full invoice payload with items
        required = ['invoice_number', 'client_id', 'items']
        for r in required:
            if r not in payload:
                return jsonify({"error": f"Missing '{r}'"}), 400

        invoice = Invoice(invoice_number=payload['invoice_number'], client_id=int(payload['client_id']), status=payload.get('status', 'DRAFT'))
        db.add(invoice)
        db.flush()

        subtotal = 0.0
        tax_total = 0.0
        for item in payload['items']:
            service_id = int(item['service_id'])
            quantity = float(item.get('quantity', 1))
            unit_price = float(item.get('unit_price'))
            tax_rate = float(item.get('tax_rate', 20.0))
            ii = InvoiceItem(invoice_id=invoice.id, service_id=service_id, quantity=quantity, unit_price=unit_price, tax_rate=tax_rate)
            db.add(ii)
            line_ht = quantity * unit_price
            line_tax = line_ht * (tax_rate / 100.0)
            subtotal += line_ht
            tax_total += line_tax

        invoice.subtotal = subtotal
        invoice.tax_total = tax_total
        invoice.total_amount = subtotal + tax_total
        db.commit()
        db.refresh(invoice)
        return jsonify({"id": invoice.id, "invoice_number": invoice.invoice_number}), 201
    finally:
        db.close()


@bp.route('/agents', methods=['GET'])
@jwt_required
def list_agents():
    # allow ADMIN/SALES/AGENT to list agents
    if getattr(request, 'current_user', None) is None:
        return jsonify({"error": "Authentication required"}), 401
    # no extra role restriction for listing

    """Return users that can act as agents. Uses users table and role field."""
    from backend.models.user import User
    db = SessionLocal()
    try:
        users = db.query(User).filter(User.is_active == True).all()
        results = [
            {"id": u.id, "email": u.email, "role": u.role}
            for u in users if (u.role or '').upper() in ('AGENT', 'SALES', 'ADMIN')
        ]
        return jsonify(results)
    finally:
        db.close()


@bp.route('/assignments', methods=['GET'])
@jwt_required
def list_assignments():
    # allow SALES/ADMIN/AGENT to view assignments; agents only see their own
    current_user = getattr(request, 'current_user', None)
    db = SessionLocal()
    try:
        from backend.models.assignment import Assignment
        rows = db.query(Assignment).order_by(Assignment.created_at.desc()).limit(100).all()
        out = []
        for a in rows:
            if current_user.role and current_user.role.upper() == 'AGENT' and a.agent_id != current_user.id:
                continue
            out.append({
                "id": a.id,
                "agent_id": a.agent_id,
                "client_id": a.client_id,
                "notes": a.notes,
                "status": a.status,
                "created_at": a.created_at.isoformat() if a.created_at else None
            })
        return jsonify(out)
    finally:
        db.close()



@bp.route('/assignments', methods=['POST'])
@jwt_required
@roles_required('ADMIN', 'SALES')
def create_assignment():
    payload = request.json or {}
    required = ['agent_id', 'client_id']
    for r in required:
        if r not in payload:
            return jsonify({"error": f"Missing '{r}'"}), 400

    db = SessionLocal()
    try:
        from backend.models.assignment import Assignment
        a = Assignment(agent_id=int(payload['agent_id']), client_id=int(payload['client_id']), notes=payload.get('notes'), status=payload.get('status', 'active'))
        db.add(a)
        db.commit()
        db.refresh(a)
        return jsonify({"id": a.id, "agent_id": a.agent_id, "client_id": a.client_id, "status": a.status}), 201
    finally:
        db.close()


# Tool call / approval workflow endpoints

@bp.route('/toolcalls/pending', methods=['GET'])
@jwt_required
def list_pending_toolcalls():
    db = SessionLocal()
    try:
        from backend.models.execution import Execution, ToolCall
        rows = db.query(ToolCall).filter(ToolCall.status == 'WAITING_APPROVAL').order_by(ToolCall.created_at.desc()).all()
        out = []
        for t in rows:
            out.append({"id": t.id, "execution_id": t.execution_id, "tool": t.tool_name, "arguments": t.arguments, "status": t.status, "created_at": t.created_at.isoformat() if t.created_at else None})
        return jsonify(out)
    finally:
        db.close()


@bp.route('/toolcalls/<int:tool_call_id>/approve', methods=['POST'])
@jwt_required
@roles_required('ADMIN','SALES')
def approve_toolcall(tool_call_id):
    db = SessionLocal()
    try:
        from backend.models.execution import ToolCall
        from backend.mcp.client import MCPClient
        tc = db.query(ToolCall).filter(ToolCall.id == tool_call_id).first()
        if not tc:
            return jsonify({"error": "ToolCall not found"}), 404
        if tc.status != 'WAITING_APPROVAL':
            return jsonify({"error": "ToolCall not awaiting approval"}), 400
        # Execute the tool using MCP client
        mcp = MCPClient()
        try:
            result = mcp.invoke(tc.tool_name, tc.arguments or {}, execution_id=tc.execution_id)
            tc.status = 'SUCCESS'
            tc.duration = 0.0
            db.commit()
            return jsonify({"success": True, "result": result})
        except Exception as e:
            tc.status = 'FAILED'
            db.commit()
            return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()


@bp.route('/quotes/<int:quote_id>/send', methods=['POST'])
@jwt_required
@roles_required('ADMIN','SALES')
def send_quote(quote_id):
    """Create a document generation toolcall for the quote and schedule email prepare/send.
    Document generation requires approval; email.send also requires approval so it's queued separately.
    Returns a tool_call id that can be approved via /toolcalls/<id>/approve
    """
    db = SessionLocal()
    try:
        quote = db.query(Quote).filter(Quote.id == quote_id).first()
        if not quote:
            return jsonify({"error": "Quote not found"}), 404
        # Build document payload
        items = db.query(QuoteItem).filter(QuoteItem.quote_id == quote.id).all()
        doc_items = []
        for it in items:
            svc = db.query(Service).filter(Service.id == it.service_id).first()
            doc_items.append({
                "description": svc.name if svc else str(it.service_id),
                "quantity": it.quantity,
                "price": it.unit_price
            })
        doc_payload = {
            "document_type": "quote",
            "client_name": quote.client.name if quote.client else "",
            "client_id": quote.client_id,
            "items": doc_items,
            "total_ht": quote.subtotal,
            "tax": quote.tax_total,
            "total_ttc": quote.total_amount,
            "reference_id": quote.id
        }
        # Create execution record
        from backend.models.execution import Execution, ToolCall
        import uuid
        exec_id = str(uuid.uuid4())
        ex = Execution(id=exec_id, session_id=None, user_id=getattr(request, 'current_user', None).id if getattr(request, 'current_user', None) else None, state='RECEIVED')
        db.add(ex)
        db.flush()
        # Create waiting tool call for document.generate
        tc = ToolCall(execution_id=exec_id, tool_name='document.generate', arguments=doc_payload, status='WAITING_APPROVAL', duration=None)
        db.add(tc)
        db.commit()
        db.refresh(tc)
        return jsonify({"execution_id": exec_id, "tool_call_id": tc.id, "status": tc.status}), 202
    finally:
        db.close()


# End of extended dashboard endpoints
