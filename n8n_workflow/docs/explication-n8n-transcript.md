# Transcription de la vidéo d'explication

Vidéo : [`explication-n8n.mp4`](explication-n8n.mp4) (5 min 23).

> **Transcription automatique, non relue.** Produite en local avec Whisper (`faster-whisper`, modèle `medium`, langue française). Les mots techniques peuvent être mal reconnus : par exemple « nodia » pour *nodes*, « Lya » pour *l'IA*, « pompes danses » pour *prompts denses*, « NPX CLI PUSH » pour `npx n8ncli push`. Seule la vidéo fait foi.

**[0:00]**  
Hello Lucas, j'espère que tu vas bien, alors du coup je te présente mon petit workflow  
Donc le but du workflow en fait c'est qu'en ce moment je me renseigne pas mal sur les outils qu'on peut trouver sur GitHub  
et mon sujet c'était que je voulais pas en installer des doublons ou des GitHub qui pourraient avoir une mauvaise influence sur des GitHub que j'ai déjà installé  
enfin sur des outils qui viennent de GitHub que j'ai déjà installé  
ou alors tout simplement quelque chose qui ne me servirait pas pour l'usage en fait dont j'ai envie de faire  
Donc ça se prend comme ça, c'est juste un petit formulaire  
On peut remplir l'URL GitHub, l'objectif, et si on doit refaire l'analyse ou pas

**[0:34]**  
Donc du coup ici, j'ai pris juste pour l'exemple un GitHub de concilia  
Je sais pas trop regarder ce que c'était en vrai, c'est juste pour l'exemple  
Du coup, une fois que je soumets le form, ça active le workflow, ça passe dans notre configuration  
Il y a tout qui est détaillé, donc les nodia que j'utilise etc  
Ensuite on descend, ici il y a le GitHub, donc ça récupère le repo, les releases  
ça lit le readme, ça regarde le project file, ensuite ça descend

**[1:09]**  
et ça regarde ici dans la database si jamais j'ai déjà scanné ce GitHub  
Si c'est le cas, alors du coup ça m'envoie directement le mail avec l'ancien recap  
puisque je peux en faire un nouveau et je peux utiliser des credits pour rien  
Si ce n'est pas le cas, ça continue, du coup ça arrive dans le personnel contexte de Notion  
Donc du coup j'ai un Notion où je renseigne tout ce que j'utilise  
Si jamais j'ai abandonné un GitHub, ce que je n'utilisais plus, si jamais j'en ai ajouté un nouveau etc  
Donc je le liste tout dedans, donc ça le compare, ça regarde ce que j'ai

**[1:43]**  
Ça prend une décision par rapport à ce que j'ai du coup  
Une fois que ça arrive là, ça agrèche tout dans un XML  
Parce que je me dis que Lya va mieux reconnaître ce que je lui demande  
Parce que forcément c'est des pompes qui sont danses, étant donné qu'il y a plein d'informations  
Donc le XML ça repère mieux  
Ensuite ça me donne tout ça, ça recrée une page dans Notion avec tout ce qu'il faut  
Pour que je puisse mettre à jour si je l'installe ou pas  
Et ça m'envoie le Gmail que je vais te montrer juste après

**[2:14]**  
Et ensuite ça se regarde dans la database  
Juste en dessous, j'ai un truc qui gère les erreurs  
Donc ça formate l'accident, juste pour que ce soit plus clair et que je reçoive un Gmail  
Et puis voilà, du coup dans Gmail  
Voilà, je l'avais déjà lancé juste avant, donc ce dépôt a déjà été analysé  
Rapport complet ici, hop ça charge  
Voilà, donc là il y a le repo avec tout ce qu'il y a dedans, le status si c'est terminé

**[2:46]**  
Un tout long did not read avec tout ce qu'il y a  
L'utilité, existance et alternatives  
Donc ça c'est là où il y aura mes repos GitHub si jamais j'en ai un qui fait la même chose  
Ici toutes les compatibilités, les conflits etc  
Et si on veut un affichage plus sympa du coup ça ressemble à ça  
Donc là on a le repart du Code Notion, c'est ce qui était là  
Les recommandations, l'intérêt principal  
L'utilité, l'existence et alternatives  
C'est là où il pourrait avoir des problèmes de compatibilité

**[3:16]**  
Donc il faut encore que je modifie quelques trucs parce que en vrai c'est un petit peu  
Comment dire  
Un petit peu restrictif parce que là ça me dit que sur un GPU ça passera pas alors qu'en réalité  
Enfin ce GitHub, j'avais déjà utilisé un similaire et ça passait donc je pense qu'il est peut-être un peu trop  
Un peu trop réfractaire à certaines choses  
Donc voilà, il y a les risques etc  
Coup du projet, si jamais j'ai besoin d'API ou autre, ça me le détaille ici  
Et là pour faire un premier essai, ça me liste à peu près les choses à faire

**[3:47]**  
Et à la fin il y a une petite note avec des étoiles sur ce qui est utile ou pas  
Voilà, pour le workflow  
Idam ici je peux le passer sur un Terminé, Repris, Arrhexaminer, Historique, Belobli  
Ça permet de garder une traçabilité  
Je me dépêche parce que j'ai plus que 56 secondes  
Pour les commandes du CLI, donc là c'est mon dossier  
Juste à faire NPX  
NPX CLI PUSH

**[4:19]**  
Dans le cas du coup ça a coupé avec le temps de l'essai gratuit LUM  
Mais du coup pour les commandes c'est NPX  
NPX CLI PUSH  
Pour récupérer les dossiers

**[4:57]**  
Donc voilà, c'est à peu près tout  
Pour les recommandations et mon avis sur le cours  
Je ne sais pas si je vais pouvoir t'en donner un parce que j'étais Freelance N8 d'avant  
Donc j'avais quand même des grosses notions  
Donc je ne pense pas avoir un avis hyper constructif à te donner  
Mais c'était quand même agréable et sympa  
Merci à toi et à la prochaine, salut !
