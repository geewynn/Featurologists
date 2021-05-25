# Datasets File Names explanation

The data has been divided in:

- Training: 2010-12-01 08:26:00 -> 2011-8-1
- Testing:  2011-8-1 -> 2011-10-1
- Live: 2011-10-1 -> 2011-12-09 12:50:00

**data.csv**: original dataset from Kaggle

**train_basket_price.csv**: pre-processed training data from the original Kaggle notebook (before clustering)

**processed_data.csv**: pre-processed training data from the original Kaggle notebook (after clustering, ready to be used for creating a model)

**test_basket_price.csv**: pre-processed testing data from the original Kaggle notebook (before scaling matrix is applied)

**live_basket_price.csv**: pre-processed data to be used as streaming source from the original Kaggle notebook (before scaling matrix is applied)

**scaled_test_matrix.csv**: pre-processed testing data from the original Kaggle notebook (after scaling matrix is applied, ready for prediction)

**scaled_live_matrix.csv**: pre-processed data to be used as streaming source from the original Kaggle notebook (after scaling matrix is applied, ready for prediction)

**no_live_data.csv**: original Kaggle dataset without all the rows which are going to be used as our live testing streaming data.

**raw_live_data.csv**: original Kaggle dataset with all the rows which are going to be used as our live testing streaming data.

**invoice_data.csv**: original SQL table containing invoices information (combining invoice_data.csv and customer_data.csv, we get no_live_data.csv which can be used in featurestore and can be divided into training and test sets for modelling. The live data is completely excluded from this.)

**customer_data.csv**: original SQL table containing customer data information  (combining invoice_data.csv and customer_data.csv, we get no_live_data.csv which can be used in featurestore and can be divided into training and test sets for modelling. The live data is completely excluded from this.)

**features.csv**: additional features created from the no_live_data.csv file in order to populate the feature store and train the secondary model for country detection.

**features_no_live_data.csv**: additional features created from the no_live_data.csv file in order to populate the feature store and train the secondary model for country detection.

**features_raw_live_data.csv**: additional features created from the raw_live_data.csv file in order to populate the feature store and test the secondary model for country detection.