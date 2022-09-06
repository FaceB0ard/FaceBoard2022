def add_template(text):
    # add text to template.txt
    with open('template.txt', 'a') as f:
        f.write("\n" + text)
    return