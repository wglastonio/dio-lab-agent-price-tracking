# Base de Conhecimento

## Dados Utilizados

Foi gerada uma lista de produtos e preços fictícios distribuídos por data, para um período de 6 meses, utilizando o Microsoft Copilot. Esses dados estão disponíveis na pasta `data`:

| Arquivo | Formato | Utilização no Agente |
|---------|---------|---------------------|
| `products_price.csv` | CSV | Histórico de preços de produtos, distribuído por data, com uma amostra no período de 6 meses. |

> [!TIP]
> **Para um dataset mais robusto** é possível integrar o Agente a APIs de preços disponibilizadas pelos varejistas, como a Selling Partner API da Amazon.

---

## Adaptações nos Dados

Como decidimos criar um Agente diferente, que não está ligado ao mercado financeiro, geramos uma lista de produtos e preços fictícios distribuídos por data, para um período de 6 meses, utilizando o Microsoft Copilot.

---

## Estratégia de Integração

### Como os dados são carregados?

Os dados disponíveis no arquivo CSV são carregados no início da sessão e incluídos no contexto do prompt.
Exemplo:

```python
import pandas as pd

# Load data source
database = pd.read_csv('./data/products_price.csv')
```

### Como os dados são usados no prompt?

No caso, os dados são carregados no início da aplicação para serem usados como contexto durante a interação entre Usuário e Agente.

---

## Exemplo de Contexto Montado

|PRODUCT_ID | DESCRIPTION | PRICE | DATE |
|-----------|-------------|-------|------|
|PROD-001 | Wireless Bluetooth Headphones | $89.99 | 01/01/2025|
|PROD-002 | Portable Power Bank 20000mAh | $42.66 | 01/06/2025
...

