{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": "null",
   "id": "9c177313",
   "metadata": {},
   "outputs": [],
   "source": [
    "html\n",
    "<!-- Modify the Register Template Layout --> {% extends 'base.html' %} \n",
    "{% block content %} \n",
    "<h2>Create a New Account</h2> \n",
    "<p>Please fill in the details below:</p> \n",
    "<form method=\"POST\"> \n",
    " {{ form.hidden_tag() }} \n",
    " <div>{{ form.email.label }}<br>{{  \n",
    "form.email(size=30) }}</div> \n",
    " <div>{{ form.password.label }}<br>{{  form.password(size=30) }}</div> \n",
    " <div>{{ form.submit(class_=\"btn\") }}</div> </form>\n"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.14.2"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
