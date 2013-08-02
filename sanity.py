import orm

def getcountrylist():
    for value in orm.session.query(orm.Value).filter(orm.Value.indID == "m49-name").all():
        yield value.region

def sql(s):
    return orm.session.execute(s).fetchmany(11)

should_be_empty = """
select distinct dsID from value where source is null; -- Blank source 
select distinct dsID from value where source is ''; -- Blank source
select distinct dsID from value where period like "%P%" and period not like "%/%"; -- Bad recurring
select distinct dsID from value where period like "%T%"; -- Bad time
select dsID from dataset where dsID not in (select dsID from value); -- Not minimal list of dsID
select indID from indicator where indID not in (select indID from value); -- Not minimal list of indID
select dsID from ("HDRStats", "World Bank", "emdat", "esa-unpd-WPP2012", "esa-unpd-WUP2011", "fao-foodsec", "faostat3", "m49", "mdgs", "unicef-infobycountry", "unterm", "who-athena", "who-athena-other", "worldbank-lending-groups") where dsID not in (select dsID from dataset); -- completeness
""".strip().split('\n')

for line in should_be_empty:
    values = sql(line)
    number = len(values)
    if number > 10: number = "many"
    if values:
        print "FAIL: %s occurrences of %r" % (number, line)
        print values
        print "------\n"
