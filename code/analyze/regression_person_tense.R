library("stargazer")

datasheet.dir <- '/nfs/turbo/si-juliame/social-movements/datasheets_for_regression_08-20-2023/'
person <- read.table(paste(datasheet.dir,'pronoun_person.tsv',sep=''),sep='\t',header=TRUE)
tense <- read.table(paste(datasheet.dir,'verb_tense.tsv',sep=''),sep='\t',header=TRUE)

person.1.model <- glm(formula= is_first ~ diagnostic + prognostic + motivational + movement,
                    family='binomial',data=person)
person.2.model <- glm(formula= is_second ~ diagnostic + prognostic + motivational + movement,
                      family='binomial',data=person)
person.3.model <- glm(formula= is_third ~ diagnostic + prognostic + motivational + movement,
                      family='binomial',data=person)
tense.model <- glm(formula= is_present ~ diagnostic + prognostic + motivational + movement,
                   family='binomial',data=tense)
out.dir <- '/nfs/turbo/si-juliame/social-movements/grammar_regression_08-20-2023/'
dir.create(out.dir,showWarnings=FALSE)

write.table(tidy(person.1.model),paste(out.dir,'person1.csv',sep=''))
write.table(tidy(person.2.model),paste(out.dir,'person2.csv',sep=''))
write.table(tidy(person.3.model),paste(out.dir,'person3.csv',sep=''))
write.table(tidy(tense.model),paste(out.dir,'tense.csv',sep=''))

stargazer(person.1.model,person.2.model,person.3.model,tense.model,
          type='latex',out=paste(out.dir,'all.tex',sep=''),
          no.space=TRUE,single.row=TRUE,star.cutoffs = c(.05,.01,.001))


stargazer(person.1.model,person.2.model,person.3.model,tense.model,
          type='text',out=paste(out.dir,'all.txt',sep=''),
          no.space=TRUE,single.row=TRUE,star.cutoffs = c(.05,.01,.001) )

