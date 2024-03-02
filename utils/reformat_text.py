from markdown import markdown

def clean_output(text):# Clean and split the text into sections
    sections = text.strip().split("\n\n")

    # Initialize an empty list to store formatted output
    formatted_text = []

    # Loop through each section
    for section in sections:
    # Check if it's a heading or itinerary content
        if section.startswith("*"):
            # Split content into bullet points
            bullet_points = section.split("\n")
            formatted_text.append("* " + "\n* ".join(bullet_points[1:]))
        else:
            # Format paragraph using markdown
            formatted_text.append(markdown(section))

        # Join all formatted sections into a single string
        formatted_text = "\n".join(formatted_text)

        # Display the formatted text in the notebook cell
    return formatted_text