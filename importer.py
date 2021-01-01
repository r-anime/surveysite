from survey.models import Anime, AnimeName, Survey, Response, AnimeResponse
from django.db.models import Q
from datetime import datetime

def import_anime(file_path):
    a = Anime.objects.all()
    answer = input('All Anime objects need to be deleted first, continue? (Y/N)')
    if answer.lower() == 'y':
        a.delete()
    else:
        return

    f = open(file_path, 'r', encoding='utf8')
    f.readline()

    anime_list = []
    animename_pair_list = []
    counter = 0

    for line in f:
        split = line.split('\t')

        type_str = split[2]
        flags = split[4]
        if type_str == '':
            anime_type = ''
        elif type_str == 'full' or type_str == 'short':
            anime_type = Anime.AnimeType.TV_SERIES
        elif type_str == 'movie':
            anime_type = Anime.AnimeType.MOVIE
        elif type_str == 'ONA':
            if 's' in flags:
                anime_type = Anime.AnimeType.ONA_SERIES
                flags = flags.replace('s', '')
            else:
                anime_type = Anime.AnimeType.ONA
        elif type_str == 'OVA':
            anime_type = Anime.AnimeType.OVA
        elif type_str == 'special':
            anime_type = Anime.AnimeType.TV_SPECIAL
        elif type_str == 'Netflix':
            anime_type = Anime.AnimeType.BULK_RELEASE
        else:
            print('Anime type unknown (' + str(type_str) + ')')
        
        if 's' in flags:
            print('Anime "' + split[0] + '" has flag "s"!')
        

        def get_year_season(year_season_org_str):
            if year_season_org_str == '':
                return None, None
            else:
                year_season_org = float(year_season_org_str)
                year = int(year_season_org)
                season = Anime.AnimeSeason(int((year_season_org - year) * 4))
                return year, season
        
        start_year, start_season = get_year_season(split[5])
        end_year, end_season = get_year_season(split[6])
        subbed_year, subbed_season = get_year_season(split[7])

        anime = Anime(
            anime_type=anime_type,
            flags=flags,
            note=split[8],
            start_year=start_year,
            start_season=start_season,
            end_year=end_year,
            end_season=end_season,
            subbed_year=subbed_year,
            subbed_season=subbed_season,
        )
        anime_list.append(anime)


        japanese_name_str = split[0].strip()
        english_name_str = split[1].strip()

        if japanese_name_str and not japanese_name_str.isspace():
            # japanese_name = AnimeName(
            #     anime_name_type=AnimeName.AnimeNameType.JAPANESE_NAME,
            #     name=japanese_name_str,
            #     official=True,
            #     anime=anime,
            # )
            # japanese_name.save()
            animename_pair_list.append({
                'anime_idx': counter,
                'name': japanese_name_str,
                'type': AnimeName.AnimeNameType.JAPANESE_NAME,
            })

        if english_name_str and not english_name_str.isspace():
            # english_name = AnimeName(
            #     anime_name_type=AnimeName.AnimeNameType.ENGLISH_NAME,
            #     name=english_name_str,
            #     official=True,
            #     anime=anime,
            # )
            # english_name.save()
            animename_pair_list.append({
                'anime_idx': counter,
                'name': english_name_str,
                'type': AnimeName.AnimeNameType.ENGLISH_NAME,
            })

        if len(anime_list) > 800: # SQLite can only handle a max of 999 variables per query
            Anime.objects.bulk_create(anime_list)
            anime_list.clear()
        
        counter += 1
    
    if len(anime_list) > 0:
        Anime.objects.bulk_create(anime_list)
    
    saved_anime_list = list(Anime.objects.all().order_by('id'))
    for anime in saved_anime_list[:50]:
        print('Anime "%s" id: %s' % (str(anime), anime.id))
    animename_list = [AnimeName(anime_name_type=pair['type'], name=pair['name'], official=True, anime=saved_anime_list[pair['anime_idx']]) for pair in animename_pair_list]
    while len(animename_list) > 0:
        AnimeName.objects.bulk_create(animename_list[:900])
        animename_list = animename_list[900:]

DEBUG = False
def find_accompanying_anime(animename_str_list):
    animename_str_list = [animename_str.strip() for animename_str in animename_str_list]
    animename_str_list = [(animename_str if animename_str.find('(') < 0 else animename_str[:animename_str.find('(')].strip()) for animename_str in animename_str_list]

    print('Finding accompanying anime for %s' % str(animename_str_list))
    queryset_filter = Q(name__startswith=animename_str_list[0])
    for animename in animename_str_list[1:]:
        queryset_filter = queryset_filter | Q(name__startswith=animename)

    animename_queryset = AnimeName.objects.filter(queryset_filter)
    anime_list = [i[0] for i in animename_queryset.values_list('anime')]
    anime_list = sorted(list(set(anime_list)))
    anime_list = [Anime.objects.get(id=id) for id in anime_list]
    if DEBUG:
        anime_list = anime_list[:1]

    if len(anime_list) == 1:
        print('Found "%s"' % anime_list[0])
        return anime_list[0]
    elif len(anime_list) > 1:
        print('Multiple matching anime found! Please pick one (or type IDxxx to manually type in an Anime ID):')
        for i in range(len(anime_list)):
            print('%i: %s' % (i, str(anime_list[i])))
        answer = input()
        try:
            answer = int(answer)
            print('Found "%s"' % anime_list[answer])
            return anime_list[answer]
        except ValueError:
            answer = int(answer[2:])
            anime = Anime.objects.get(id=answer)
            print('Found "%s"' % anime)
            return anime
    else:
        print('No matching anime found! Please type in an Anime ID or "N" to cancel')
        if DEBUG:
            answer = 'N'
        else:
            answer = input()

        try:
            answer = int(answer)
            anime = Anime.objects.get(id=answer)
            print('Found "%s"' % anime)
            return anime
        except ValueError:
            print('Returning None')
            return None

# Converts e.g. what was originally a "watching" table cell into a list of Anime objects
def parse_anime_strlist(anime_strlist, str_to_anime_map):
    anime_list = []
    
    while anime_strlist:
        found = False
        for anime_series_str in sorted(list(str_to_anime_map.keys()), key=lambda anime_series_str: len(anime_series_str), reverse=True):
            if anime_strlist.find(anime_series_str) == 0:
                anime_series = str_to_anime_map[anime_series_str]
                if anime_series:
                    anime_list.append(anime_series)

                if len(anime_strlist) > len(anime_series_str):
                    comma_idx = anime_strlist.index(', ', len(anime_series_str))
                    anime_strlist = anime_strlist[comma_idx+2:]
                else:
                    anime_strlist = ''

                found = True
                break
        
        if not found:
            try:
                anime_strlist = anime_strlist[anime_strlist.index(', ')+2:]
            except:
                anime_strlist = ''
    
    return anime_list

def add_survey(survey_file_path, survey_anime_file_path, year, quarter, is_preseason):
    survey_queryset = Survey.objects.filter(year=year, season=quarter, is_preseason=is_preseason)
    if len(survey_queryset) > 0:
        survey = survey_queryset[0]
        print('Found survey: "%s"' % survey)
        deletion_count, deletion_dict = Response.objects.filter(survey=survey).delete()
        print('Deleted %i responses: %s' % (deletion_count, str(deletion_dict)))
    else:
        survey = Survey(
            year=year,
            season=quarter,
            is_preseason=is_preseason,
            is_ongoing=False,
        )
        survey.save()
        print('Created a new survey: "%s"' % survey)
    

    # +------------------+
    # | GET SURVEY ANIME |
    # +------------------+
    print('Reading survey anime')
    fa = open(survey_anime_file_path, 'r', encoding='utf8')
    fa.readline()
    
    anime_series_map = {}
    special_anime_map = {}
    for line in fa:
        split = line.split('\t')
        series_str = split[0].strip()
        if series_str and not series_str.isspace():
            anime_series = find_accompanying_anime(series_str.split(' | '))
            anime_series_map[series_str] = anime_series
        
        special_str = split[1].strip()
        if special_str and not special_str.isspace():
            special_anime = find_accompanying_anime(special_str.split(' | '))
            special_anime_map[special_str] = special_anime

    
    # +---------------------+
    # | READ SURVEY RESULTS |
    # +---------------------+
    print('Reading survey results')
    f = open(survey_file_path, 'r', encoding='utf8')
    headers = f.readline().split('\t')

    animeresponse_list = []

    line_ctr = 2
    for line in f:
        split = line.split('\t')

        # +-----------------+
        # | CREATE RESPONSE |
        # +-----------------+
        timestamp_str = split[0]
        date_split = timestamp_str.split(' ')[0].split('/')
        time_split = timestamp_str.split(' ')[1].split(':')
        timestamp = datetime(
            year=int(date_split[2]),
            month=int(date_split[0]),
            day=int(date_split[1]),
            hour=int(time_split[0]),
            minute=int(time_split[1]),
            second=int(time_split[2]),
        )

        age_str = split[1]
        age = float(age_str) if age_str != '' else None

        gender_str = split[2]
        if gender_str == 'Male':
            gender = Response.Gender.MALE
        elif gender_str == 'Female':
            gender = Response.Gender.FEMALE
        elif gender_str == 'Other':
            gender = Response.Gender.OTHER
        else:
            gender = None

        response = Response(
            timestamp=timestamp,
            survey=survey,
            age=age,
            gender=gender
        )
        response.save()


        # +-------------------------+
        # | GENERATE ANIMERESPONSES |
        # +-------------------------+
        animeresponse_map = {
            anime: AnimeResponse(anime=anime, response=response, watching=False, underwatched=False) for anime in list(anime_series_map.values()) + list(special_anime_map.values()) if anime is not None
        }
        
        # Get watching anime
        watching_anime_str = split[3]
        watching_anime_list = parse_anime_strlist(watching_anime_str, anime_series_map)
        for anime in watching_anime_list:
            animeresponse_map[anime].watching = True

        # Get underwatched anime if post-season
        if not survey.is_preseason:
            underwatched_anime_str = split[4]
            underwatched_anime_list = parse_anime_strlist(underwatched_anime_str, anime_series_map)
            for anime in underwatched_anime_list:
                animeresponse_map[anime].underwatched = True
        


        header_idx = 4 if survey.is_preseason else 5

        # Get anime scores
        while headers[header_idx].startswith('How good '):
            header = headers[header_idx]

            start = header.index('[')
            end = header.rindex(']')
            anime_str = header[start+1:end].strip()
            anime = anime_series_map[anime_str]

            anime_score_str = split[header_idx]
            if anime and anime_score_str and not anime_score_str.isspace() and anime_score_str != 'N/A':
                anime_score = int(anime_score_str[0])
                animeresponse_map[anime].score = anime_score

            header_idx += 1
        
        # Get surprises/disappointments
        while headers[header_idx].startswith('What are your '):
            header = headers[header_idx]

            start = header.index('[')
            end = header.rindex(']')
            anime_str = header[start+1:end]
            anime = anime_series_map[anime_str].strip()

            expectations_str = split[header_idx]
            if anime and expectations_str and not expectations_str.isspace() and expectations_str != 'N/A':
                expectations = AnimeResponse.Expectations.SURPRISE if expectations_str == 'Surprise' else AnimeResponse.Expectations.DISAPPOINTMENT
                animeresponse_map[anime].expectations = expectations
            
            header_idx += 1
        

        # Get watching special anime
        watching_special_anime_str = split[header_idx]
        watching_special_anime_list = parse_anime_strlist(watching_special_anime_str, special_anime_map)
        for anime in watching_special_anime_list:
            animeresponse_map[anime].watching = True
        
        
        # Get special anime scores
        while headers[header_idx].startswith('How good '):
            header = headers[header_idx]

            start = header.index('[')
            end = header.rindex(']')
            anime_str = header[start+1:end]
            anime = special_anime_map[anime_str].strip()

            anime_score_str = split[header_idx]
            if anime and anime_score_str and not anime_score_str.isspace() and anime_score_str != 'N/A':
                anime_score = int(anime_score_str[0])
                animeresponse_map[anime].score = anime_score

            header_idx += 1


        # Filter and save AnimeResponses
        for animeresponse in animeresponse_map.values():
            if survey.is_preseason:
                keep_animeresponse = animeresponse.watching == True or animeresponse.score is not None
            else:
                keep_animeresponse = animeresponse.watching == True

            if keep_animeresponse:
                animeresponse_list.append(animeresponse)
        
        # Bulk create for performance (SQLite only allows max 999 variables per query, >800 to be safe)
        if len(animeresponse_list) > 800:
            AnimeResponse.objects.bulk_create(animeresponse_list)
            animeresponse_list.clear()

        print('Parsed response %i: "%s: %s %s, %s watching, %s special watching"' % (line_ctr, str(timestamp), str(age) if age is not None else '----', str(gender) if gender is not None else '-', str(len(watching_anime_list)), str(len(watching_special_anime_list))))
        line_ctr += 1
        #print('Watching anime: %s' % str('\n'.join([str(anime) for anime in watching_anime_list])))

        # answer = input('Continue? (Y/N) ')
        # if answer.lower() == 'n':
        #     break
    
    AnimeResponse.objects.bulk_create(animeresponse_list)
    animeresponse_list.clear()

