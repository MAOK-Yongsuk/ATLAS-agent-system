# Introduction to Machine Learning

## Chapter 1: Fundamentals

### 1.1 What is Machine Learning?
Machine learning is a branch of artificial intelligence that enables systems to learn and improve from experience automatically. It focuses on developing computer programs that can access data and use it to learn for themselves.

Key Points:
- Automated learning from data
- Pattern recognition
- Predictive modeling
- Decision making

### 1.2 Types of Machine Learning

#### Supervised Learning
- Classification
  * Binary classification
  * Multi-class classification
- Regression
  * Linear regression
  * Polynomial regression

#### Unsupervised Learning
- Clustering
  * K-means
  * Hierarchical clustering
- Dimensionality Reduction
  * PCA
  * t-SNE

### 1.3 Core Concepts
1. Training Data
2. Test Data
3. Validation
4. Model Evaluation
5. Hyperparameter Tuning

## Practice Questions
1. What is the difference between supervised and unsupervised learning?
2. Explain the importance of splitting data into training and test sets.
3. Describe three common applications of machine learning in real world.

## Coding Examples
```python
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

# Sample code
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
model = LinearRegression()
model.fit(X_train, y_train)
```