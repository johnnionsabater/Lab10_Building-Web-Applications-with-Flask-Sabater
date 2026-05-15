dashboard_template = '''{% extends "base.html" %}
{% block title %}Dashboard{% endblock %}
{% block content %}
<section class="card">
    <h2>Dashboard</h2>

    {% if user.image_filename %}
    <img
        src="{{ url_for('static', filename='uploads/' + user.image_filename) }}"
        alt="Profile Picture"
        width="120"
    >
    {% endif %}

    <p><strong>Name:</strong> {{ user.display_name }}</p>
    <p><strong>Email:</strong> {{ user.email }}</p>
    <form method="POST" action="{{ url_for('update_profile') }}" enctype="multipart/form-data">
        {{ form.hidden_tag() }}

        <label for="display_name">{{ form.display_name.label.text }}</label>
        {{ form.display_name(id="display_name", placeholder="Enter your display name") }}

        <label for="profile_image">{{ form.profile_image.label.text }}</label>
        {{ form.profile_image(id="profile_image", accept=".jpg,.jpeg,.png") }}

        {{ form.submit(class_="btn") }}
    </form>
</section>
{% endblock %}
'''
