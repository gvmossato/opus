***

<p align="center">
  <img src="https://i.ibb.co/QbRBhdq/logo.png" alt="opus-logo" width="500px" />
</p>

<p align="center">  
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python%203.12-3776AB?style=for-the-badge&logo=python&logoColor=yellow&color=3776AB" alt="python-badge" />
  </a>
  <a href="https://www.djangoproject.com/">
    <img src="https://img.shields.io/badge/Django%205.0.6-gree?style=for-the-badge&logo=django&logoColor=white" alt="django-badge" />
  </a>
  <a href="https://github.com/gvmossato/opus/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/gvmossato/opus?color=blue&style=for-the-badge" alt="license-badge" />
  </a>
</p>
 
***

<p align="center">
  <a href="#-about">📚 About</a> | 
  <a href="#-site">🌎 Site</a>   | 
  <a href="#-getting-started">🚀 Getting Started</a> |
  <a href="#-collaborators">🧙 Collaborators</a>
</p>

<p align="center">
  Opus began as a college project for an Information Systems course and evolved into a collaborative productivity tool. It allows users to organize their to-do lists with the help of friends, coworkers, and even new acquaintances on the platform!
</p>
  
<h4 align="center">
  :star: Liked? Give us a star! :star:
</h4>
 
## 📚 About

<p>
  <img src="https://i.ibb.co/37DmPv3/opus-about.png" alt="about" />
</p>

Our main goal with Opus is to make staying organized enjoyable rather than a chore. We believe in **splitting tasks**, **joining forces**, and **eliminating rework** to achieve this.

### Split the Tasks

When creating your to-do lists, have you ever considered that others might have the same tasks to accomplish? Whether you're in school, college, or already working, this is often the case.

This is where Opus shines: you can create a to-do list and invite your colleagues to collaborate. You can assign roles, determining who can invite new members and create tasks, and who can simply view the tasks that need to be done.

### Join the Forces

With everyone knowing their responsibilities, you no longer need to stress about remembering all the projects and assignments you have. A friend can handle one subject while you cover another, resulting in half the effort for all the tasks.

Taking a trip or some days off? No problem! Promote others from your list to help keep things organized, ensuring you don't return to a backlog of tasks.

### Eliminate the Rework

Invited to a list but missing some tasks important to you? Or perhaps you don't need to see every task on the list? Don't waste time recreating what matters on your list.

Opus allows you to copy tasks by tags you're interested in to a list you have permissions for, and it doesn't stop there:

* The tasks become yours, so you can edit the details as you wish!
* New tasks with the chosen tags will automatically sync from the original list to yours upon creation!

## 🌎 Site

To get started with Opus, simply create an account:

<img src="https://i.ibb.co/RcQXZBg/1-1-Homepage-Registrar-2x.png" alt="signup" />

And log in:

<img src="https://i.ibb.co/dBSwv3C/1-2-Homepage-Entrar-2x.png" alt="signin" />

After that, you are free to edit your profile as you like:

<img src="https://i.ibb.co/tz8q98W/2-1-Perfil-Configura-es-2x.png" alt="edit-profile" />

From there, just create a list:

<img src="https://i.ibb.co/qJ1JMnz/2-2-Perfil-Criar-lista-2x.png" alt="create-list" />

And start managing your tasks:

<img src="https://i.ibb.co/RS5jbB5/3-1-Lista-Vis-o-do-Administrador-2x.png" alt="list-administrator" />

Oh, and don't forget! Collaboration is the essence of Opus, so invite and manage users as you see fit:

<img src="https://i.ibb.co/NNfpW2h/3-4-Lista-Gerenciar-Usu-rios-2x.png" alt="social" />

We'll notify you of all the list invitations you receive:

<p align="center">
  <img src="https://i.ibb.co/j8H0SMS/2-Perfil-2x.png" alt="invites" width="450px" />
</p>

And you only need to indicate what interests you from there:

<img src="https://i.ibb.co/fn54WNv/3-5-Lista-Seguir-Lista-1-2-2x.png" alt="follow-list-tags" />

To bring them into your lists:

<img src="https://i.ibb.co/2ZPRj7Z/3-5-Lista-Seguir-Lista-2-2-2x.png" alt="follow-list-target" />

## 🚀 Getting Started

Although it may not be evident from this repository, Opus was never officially launched. However, it was deployed in production via [Heroku](https://www.heroku.com/), utilizing the now-defunct free tier. Despite being just a college project, we achieved all the essential functionalities of the application, including user creation with email authentication tokens, list management with different user permissions, and automatic task sharing between followed lists.

If you're interested in running the application locally, you need to install [Python Development Master](https://pdm-project.org/en/latest/) (PDM). It's also recommended to use [Pyenv](https://github.com/pyenv/pyenv) (optional).

Once you have the required packages installed, clone this repository and install the dependencies (Python 3.12 is expected):

```
pdm install
```

Next, create a `.env` file in the same directory as the [template](https://github.com/gvmossato/opus/blob/main/opus/settings/.env.example) with the environment variables and run the database migrations:

```
pdm run migrations
```


Finally, handle the static files using:

```
pdm run collect_static
```

All set! Start the server by running:

```
pdm run start
```

While developing, if any models modifications are made, you will need to execute `pdm run make_migrations` and then apply the `migrations` script.

> [!NOTE]
> After this first initial setup you can always start the server by executing the `start` script.

## 🧙 Collaborators

This project was originally made possible through the direct work of:

* [Gabriel Mossato](https://github.com/gvmossato)
* [Henrique Ken](https://github.com/HenriqueKen)
* [Higor Silva](https://github.com/Higor-Silva1)
* [Paulino Veloso](https://github.com/pfvelu)

With a special thanks for the support given by:

* [André Kubagawa Sato](https://scholar.google.com.br/citations?user=NFMTwSwAAAAJ)
* [Marcos de Sales Guerra Tsuzuki](https://scholar.google.com.br/citations?user=nXAxC7UAAAAJ)
