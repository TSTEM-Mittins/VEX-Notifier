from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.probability import FreqDist

def text_summarizer(text, num_sentences=10):
    # Text into sentences
    sentences = sent_tokenize(text)
    
    # Text into words
    words = word_tokenize(text.lower())
    
    # Removing stop words
    stop_words = set(stopwords.words("english"))
    filtered_words = [word for word in words if word.casefold() not in stop_words]
    
    # Calculate word frequencies
    fdist = FreqDist(filtered_words)
    
    # Assign scores to sentences based on word frequencies
    sentence_scores = {}
    for i, sentence in enumerate(sentences):
        for word in word_tokenize(sentence.lower()):
            if word in fdist:
                if i in sentence_scores:
                    sentence_scores[i] += fdist[word]
                else:
                    sentence_scores[i] = fdist[word]
    
    # Sort sentences by scores in descending order
    sorted_sentences = sorted(sentence_scores, key=lambda x: sentence_scores[x], reverse=True)
    
    # Select the top `num_sentences` sentences for the summary
    summary_sentences = sorted(sorted_sentences[:num_sentences])
    
    # Create the summary
    summary = ' '.join([sentences[i] for i in summary_sentences])
    
    return summary

#   This is not my script, credit goes to - https://github.com/colombomf/text-summarizer
