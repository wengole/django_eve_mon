from django.core.management import BaseCommand
from evelink.eve import EVE
from tqdm import tqdm
from ...models import Group, Skill, Requirement, Attribute


class Command(BaseCommand):
    args = ""
    help = ""

    def handle(self, *args, **options):
        eve = EVE()
        r = eve.skill_tree()
        skills = {}
        for group in r[0].values():
            print "Import group: %s" % group['name']
            grp, _ = Group.objects.get_or_create(
                id=group['id'],
                name=group['name']
            )
            for skill in tqdm(group['skills'].values()):
                skills[skill['id']] = skill
                try:
                    Skill.objects.get(
                        id=skill['id'],
                        name=skill['name']
                    )
                except Skill.DoesNotExist:
                    # Create the skill if it does not exist
                    pass
                else:
                    # Otehrwise we can skip importing this one
                    continue
                skl = Skill(
                    id=skill['id'],
                    name=skill['name'],
                    published=skill['published'],
                    rank=skill['rank'],
                    description=skill['description'],
                    group=grp,
                )
                attr, _ = Attribute.objects.get_or_create(
                    name=skill['attributes']['primary'] or ''
                )
                skl.primary_attribute = attr
                attr, _ = Attribute.objects.get_or_create(
                    name=skill['attributes']['secondary'] or ''
                )
                skl.secondary_attribute = attr
                skl.save()

        print "Populating Requirement table"
        for skill in tqdm(skills.values()):
            skl = Skill.objects.get(id=skill['id'])
            for req_skill in skill['required_skills'].values():
                rskl = Skill.objects.get(id=req_skill['id'])
                requirement, _ = Requirement.objects.get_or_create(
                    skill=rskl,
                    level=req_skill['level']
                )
                skl.required_skills.add(requirement)
                skl.save()