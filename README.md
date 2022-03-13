The goal of this mini project is to extract bigrams and phrases from Hebrew short stories, and try to recognize patterns over the stories release dates.
Using the Ben-Yehuda dump:
https://github.com/projectbenyehuda/public_domain_dump
Together with the of mapping short stories on the said dump:
https://github.com/kerentz/Mapping-Ben-Yehuda-project

as the projects dataset.
To run:
1) Copy the whole dump into the project root folder.
2) Run main.py with flag --interval , indicating the wanted year interval to partition by
3) Output will be txt files for both raw count of the top bigrams and the top pmi scores.