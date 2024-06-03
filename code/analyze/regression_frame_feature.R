
datasheet.dir <- "/nfs/turbo/si-juliame/social-movements/datasheets_for_regression_08-18-2023/"

pronoun.number.file <- paste(datasheet.dir, "pronoun_number.tsv", sep="")
pronoun.number <- read.table(pronoun.number.file, header=TRUE, sep="\t")

pronoun.person.file <- paste(datasheet.dir, "pronoun_person.tsv", sep="") 
pronoun.person <- read.table(pronoun.person.file, header=TRUE, sep="\t")

verb.tense.file <- paste(datasheet.dir, "verb_tense.tsv", sep="")
verb.tense <- read.table(verb.tense.file, header=TRUE, sep="\t")

print(head(pronoun.number))