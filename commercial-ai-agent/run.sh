#!/bin/bash

# Exit on error
set -e

echo "=========================================="
echo "🚀 Initialisation du projet Commercial AI"
echo "=========================================="

# 1. Vérifier et installer Ollama si nécessaire
if ! command -v ollama &> /dev/null; then
    echo "📦 Ollama n'est pas installé. Installation en cours..."
    curl -fsSL https://ollama.com/install.sh | sh
    echo "✅ Ollama installé avec succès."
else
    echo "✅ Ollama est déjà installé."
fi

# Démarrer Ollama en arrière-plan si ce n'est pas déjà le cas
if ! pgrep -x "ollama" > /dev/null; then
    echo "🔄 Démarrage du service Ollama..."
    ollama serve > /dev/null 2>&1 &
    sleep 3 # Attendre que le service démarre
fi

# 2. Télécharger les modèles requis
echo "🧠 Vérification et téléchargement des modèles d'IA..."
MODELS=("qwen3:14b" "gemma4:e4b-mlx" "deepseek-r1:8b" "granite4.1-guardian:8b")

for model in "${MODELS[@]}"; do
    echo "Vérification du modèle : $model"
    # Vérifier si le modèle existe déjà pour éviter de le retélécharger inutilement
    if ! ollama list | grep -q "$model"; then
        echo "⬇️ Téléchargement de $model (cela peut prendre du temps)..."
        ollama pull "$model" || echo "⚠️ Erreur lors du téléchargement de $model. Assurez-vous que le nom est correct."
    else
        echo "✅ Modèle $model déjà présent."
    fi
done

# 3. Configuration du Backend (Python)
echo "🐍 Configuration du backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "Création de l'environnement virtuel (venv)..."
    python3 -m venv venv
fi

echo "Activation de l'environnement virtuel..."
source venv/bin/activate

echo "📦 Installation des dépendances..."
pip install --upgrade pip
pip install -r requirements.txt

# 4. Lancement du Backend
echo "🚀 Lancement du serveur backend..."
python run.py
