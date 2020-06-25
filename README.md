# SEC 10K, 10Q Filings Sentiment Index 

### Motivation
SEC filings are a great information source for investing. By estimating sentiment in these filings with the state of the art of nlp, [BERT](https://arxiv.org/abs/1810.04805), can we build a portfolio that outperform SP500? 


### Methdology
The repo scraps 10K and 10Q SEC filings of SP500 companies, runs sentiment analysis with [FinBERT](https://arxiv.org/pdf/1908.10063.pdf) on
  - Item 1A. Risk Factors 
  - Item 7. Management’s Discussion and Analysis of Financial Condition and Results of Operations Item
  - Item 7A. Quantitative and Qualitative Disclosures about Market Risk
of, weights the sentences sentiment scores with [summa](https://github.com/summanlp/textrank), built portfolio based on 
 1. each item's sentiment score
 2. weighted sentiment score of all items
 
Portfolio Index Weighting Schemes
 a. long-short on ranked sentiment
 b. proportioal to sentiment
 c. inverse of sentiment
 d. minimum variance 
 e. maximum Sharpe
 f. target variance
