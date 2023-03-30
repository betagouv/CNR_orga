# CNR Orga

L'application web qui soutient les organisateurs de CNR (Conseil National de la Refondation).

## Lancement en local avec Docker

### Prérequis

- Docker 19.03.0+
- `docker-compose` ([installation standalone](https://docs.docker.com/compose/install/other/))

### Copier les variables d'environnement

Le fichier `.env.example` contient des variables fonctionnelles pour un **environnement de test** Docker.

```sh
cp .env.example .env
```

### Lancer les containeurs

```sh
docker-compose up -d
```

### Accéder à l'application

Dans le navigateur : `http://localhost:8000/accounts/login/`

Et pour lire les mails : `http://localhost:8025/`
