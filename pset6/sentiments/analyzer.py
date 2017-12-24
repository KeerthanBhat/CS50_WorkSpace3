import nltk

class Analyzer():
    """Implements sentiment analysis."""

    def __init__(self, positives, negatives):
        """Initialize Analyzer."""
        # loads the text files with words into lists
        
        # initialize lists
        self.positives = []
        self.negatives = []
        
        # open file with positive words
        with open(positives) as lines:
            for line in lines:
                # if not starting with ; or space
                if not line.startswith((";", " ")):
                    self.positives.extend(line.rsplit("\n"))
                    
        with open(negatives) as lines:
            for line in lines:
                if not line.startswith((";", " ")):
                    self.negatives.extend(line.rsplit("\n"))
                

    def analyze(self, text):
        """Analyze text for sentiment, returning its score."""

        # breaks the tweet sent into words/tokens
        tokenizer = nltk.tokenize.TweetTokenizer()
        tokens = tokenizer.tokenize(text)
        
        score = 0
        
        # for each word in the tweet
        for token in tokens:
            
            # calculates the score
            # convert all cases to lower case using lower()
            if token.lower() in self.positives:
                score = score + 1
            elif token.lower() in self.negatives:
                score = score - 1
        
        # returns the score
        return score
