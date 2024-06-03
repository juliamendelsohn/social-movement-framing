library("stargazer")
library(tidyverse)
library(margins)
library(broom)
library(multcomp)
datasheet.file <- '/nfs/turbo/si-juliame/social-movements/full_corpus_with_preds_and_stakeholders_08-02-2023.tsv'

df <- read.table(datasheet.file,sep='\t',header=TRUE,fill=TRUE, quote="",comment.char="")
df <- df[df['Task1.relevance']==1,]

colnames(df)[colnames(df) == 'Task3.diagnostic'] <- 'diagnostic'
colnames(df)[colnames(df) == 'Task3.prognostic'] <- 'prognostic'
colnames(df)[colnames(df) == 'Task5.motivational.elements'] <- 'motivational'
colnames(df)[colnames(df) == 'Task3.identify'] <- 'identify'
colnames(df)[colnames(df) == 'Task3.blame'] <- 'blame'
colnames(df)[colnames(df) == 'Task4.solution'] <- 'solution'
colnames(df)[colnames(df) == 'Task4.tactics'] <- 'tactics'
colnames(df)[colnames(df) == 'Task4.solidarity'] <- 'solidarity'


df$stance <- with(df, ifelse(
  Task2.stance == 0, 'conservative', ifelse(
  Task2.stance == 1, 'neutral', ifelse(
  Task2.stance == 2, 'progressive','NA'))))

df$interaction <- with(df, ifelse(
  is_quote == 1, 'quote', ifelse(
  is_reply == 1, 'reply', 'broadcast'
  )))

df$issue <- df$movement

df$issue <- relevel(as.factor(df$issue), ref = 'guns')
df$stance <- relevel(as.factor(df$stance), ref = 'neutral')
df$protest_activity <- relevel(as.factor(df$protest_activity), ref = 'avg')
df$interaction <- relevel(as.factor(df$interaction), ref = 'broadcast')
df$stakeholder_group <- relevel(as.factor(df$stakeholder_group), ref = 'other')


dvs <- c("diagnostic","prognostic","motivational",
         "identify","blame","solution","tactics","solidarity")


out.dir <- '/home/juliame/social-movements/results/sociocultural_regression_09-27-2023/'
dir.create(out.dir,showWarnings=FALSE)

suffix <- '_no_stance'

models <- list()
all.p.values <- c()

for(i in 1:length(dvs)){
  if(suffix=='_with_stance'){
  fm <- as.formula(paste(dvs[[i]],'~ issue+stance+protest_activity+stakeholder_group+interaction',sep=''))
  } else{
    fm <- as.formula(paste(dvs[[i]],'~ issue+protest_activity+stakeholder_group+interaction',sep=''))
  }
  model <- glm(fm,family=binomial(link='logit'), data=df)
  models[[i]] <- model
  model.margins <- margins(model)
  
  all.p.values <- c(all.p.values,tidy(model)$p.value)
  write.table(tidy(model),paste(out.dir,dvs[[i]],suffix,'.tsv',sep=''),sep='\t')
  write.table(summary(model.margins),paste(out.dir,dvs[[i]],suffix,'_margins.tsv',sep=''),sep='\t')
}

corrected.p.values <- p.adjust(all.p.values,method='holm')
num.models <- length(models)
num.vars <- nrow(tidy(models[[1]]))
corrected.p.values.list <- split(corrected.p.values,rep(1:num.models,each=num.vars))

for(i in 1:length(dvs)){
  model <- models[[i]]
  dv <- dvs[[i]]
  res <- tidy(model)
  orig.p <- res$p.value
  corrected.p <- corrected.p.values.list[[i]]
  res$corrected.p.value <- corrected.p
  #write.table(res,paste(out.dir,dv,suffix,'.tsv',sep=''),sep='\t')
}

#stargazer(models,
#          type='text',p=corrected.p.values.list,
#          no.space=TRUE,single.row=TRUE,star.cutoffs = c(.05,.01,.001),report=('vc*'),
#          out=paste(out.dir,'regression',suffix,'_text.txt',sep=''))


#stargazer(models,corrected.p.values.list,
#          no.space=TRUE,single.row=TRUE,star.cutoffs = c(.05,.01,.001),report=('vc*'),
#          out=paste(out.dir,'regression',suffix,'_latex.tex',sep=''))





