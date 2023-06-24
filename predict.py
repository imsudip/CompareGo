import pickle
with open('logreg_model.pkl', 'rb') as file:
     model = pickle.load(file)
with open('tfidf.pkl', 'rb') as file:
    cv = pickle.load(file)
def predictReview(comment):
    t=comment
    t_e=cv.transform([t]).toarray()
    test = model.predict_proba(t_e)
    pr=test[0][1]
    if pr<0.2:
        return 1
    elif pr<0.4:
        return 2
    elif pr<0.6:
        return 3
    elif pr<0.8:
        return 4
    else:
        return 5
    
print(predictReview("i love this product"))