
def get_title(member):
    return member.title


def get_email(member):
    return member.email


def get_name(member):
    return member.name


def get_avatar(member):
    return member.avatar


def get_phone(member):
    return member.phone


SCOPES = {
    'title': get_title,
    'email': get_email,
    'name': get_name,
    'avatar': get_avatar,
    'phone': get_phone,
}

