from scrapy.item import Item, Field


class OpportunityItem(Item):
    feed = Field()  # URL of webpage or RSS feed
    title = Field()
    uri = Field()  # URL or RSS GUID
    description = Field()
    location = Field()  # Raw location
    country = Field()
    region = Field()
    department = Field()
    city = Field()
    address = Field()
    postal_code = Field()
    website = Field()
    email = Field()
    phone_number = Field()  # For now: "01 23 45 67 89"
    start_date_day = Field()  # dd
    start_date_month = Field()  # mm
    start_date_year = Field()  # YYYY
    end_date_day = Field()
    end_date_month = Field()
    end_date_year = Field()
    duration_min = Field()
    duration_max = Field()
    client = Field()  # Group or person
    client_activity = Field()
    contact = Field()  # Person
    category = Field()
    skills = Field()
    target = Field()
    type = Field()
