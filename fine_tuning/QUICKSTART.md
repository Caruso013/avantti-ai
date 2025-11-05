# 🎯 Quick Start - Fine-Tuning em 3 Passos

## 📋 Passo 1: Preparar Dados
```bash
python fine_tuning/prepare_training_data.py
```
✅ **Resultado:** Arquivo `training_data.jsonl` criado

---

## 🚀 Passo 2: Iniciar Treinamento
```bash
python fine_tuning/upload_and_train.py
```
✅ **Resultado:** Job ID (ex: `ftjob-abc123`)

---

## 👀 Passo 3: Monitorar
```bash
python fine_tuning/monitor_training.py ftjob-abc123 --watch
```
✅ **Resultado:** Model ID quando concluído (ex: `ft:gpt-4o-mini-2024-07-18:avantti:evex-eliane:abc123`)

---

## 🔧 Usar o Modelo

**Editar:** `src/services/openai_service.py` (linha ~417)

**Antes:**
```python
"model": "gpt-4o-mini"
```

**Depois:**
```python
"model": "ft:gpt-4o-mini-2024-07-18:avantti:evex-eliane:abc123"
```

---

## 🧪 Testar (Opcional)
```bash
python fine_tuning/test_model.py
```

---

## 💰 Custos
- **Treinamento:** ~$0.15 a $0.50 (dependendo do volume)
- **Uso:** 50% mais barato que GPT-4o-mini base

---

## 📚 Documentação Completa
Veja `fine_tuning/README.md` para detalhes completos.
