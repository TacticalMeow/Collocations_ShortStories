class Bigramdict:
  def __init__(self, colloc_dict, w1_dict,w2_dict,pmi_dict,bigram_count):
    self.colloc_dict = colloc_dict
    self.w1_dict = w1_dict
    self.w2_dict = w2_dict
    self.pmi_dict = pmi_dict
    self.bigram_count =bigram_count
    