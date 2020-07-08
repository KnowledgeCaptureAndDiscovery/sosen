from sklearn.feature_extraction.text import CountVectorizer


class KeywordCounter:

    def __init__(self, ids, documents):
        self.ids = ids
        # https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.CountVectorizer.html
        vectorizer = CountVectorizer(stop_words="english")
        tokens = vectorizer.fit_transform(documents)
        self.keyword_names = vectorizer.get_feature_names()
        self.keyword_count_array = tokens.toarray()
        self.keyword_length = len(self.keyword_names)
        self.doc_length = len(ids)

    def get_keyword_data(self):
        keyword_document_counts = [sum([1 if self.keyword_count_array[doc_index][keyword_index] > 0 else 0
                                        for doc_index in range(self.doc_length)])
                                   for keyword_index in range(self.keyword_length)
                                   ]

        return {
            self.keyword_names[i]: keyword_document_counts[i]
            for i in range(self.keyword_length)
        }

    def get_keyword_relationship_data(self):
        return {
            self.ids[doc_index]: {
                "keywords": [
                    {
                        "label": self.keyword_names[keyword_index],
                        "count": keyword_count
                    }
                    for keyword_index, keyword_count in enumerate(keyword_count_row)
                    if keyword_count > 0
                ],
                "count": sum(keyword_count_row)
            }
            for doc_index, keyword_count_row in enumerate(self.keyword_count_array)
        }

class ExistingKeywordCounter:

    def __init__(self, id_keyword_dict):
        self.id_keyword_dict = id_keyword_dict

    @staticmethod
    def make_list(maybe_list):
        if isinstance(maybe_list, list) or isinstance(maybe_list, tuple):
            return maybe_list
        else:
            return [maybe_list]

    def get_keyword_data(self):
        keyword_data = {}
        for keyword_list in self.id_keyword_dict.values():
            keyword_list = ExistingKeywordCounter.make_list(keyword_list)

            for keyword in keyword_list:
                if keyword not in keyword_data:
                    keyword_data[keyword] = 0

                keyword_data[keyword] += 1

        return keyword_data

    def get_keyword_relationship_data(self):
        return {
            doc_id: {
                "keywords": [
                    {
                        "label": keyword,
                        "count": 1
                    }
                    for keyword in keyword_list
                ],
                # keywords are unique, so the count is the length
                "count": len(keyword_list)
            }
            for doc_id, keyword_list in
            (
                ( doc_id, ExistingKeywordCounter.make_list(keyword_list))
                for doc_id, keyword_list in self.id_keyword_dict.items()
            )
        }



