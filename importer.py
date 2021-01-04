from survey.models import Anime, AnimeName, Survey, Response, AnimeResponse, SurveyAdditionRemoval
from django.db.models import Q
from datetime import datetime
import re
import os

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
            animename_pair_list.append({
                'anime_idx': counter,
                'name': japanese_name_str,
                'type': AnimeName.AnimeNameType.JAPANESE_NAME,
            })

        if english_name_str and not english_name_str.isspace():
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
    
    # This is why all the Anime objects need to be deleted first
    # All Anime objects created before are cached and do not contain IDs, so they have I get all the anime from the DB again
    saved_anime_list = list(Anime.objects.all().order_by('id'))
    animename_list = [AnimeName(anime_name_type=pair['type'], name=pair['name'], official=True, anime=saved_anime_list[pair['anime_idx']]) for pair in animename_pair_list]

    while len(animename_list) > 0:
        AnimeName.objects.bulk_create(animename_list[:900])
        animename_list = animename_list[900:]






def add_multiple_surveys(folder_path):
    # Reads multiple surveys from a folder
    # File names have to be formatted the following way:
    #   (yyyy)-(s)-(pre/post).tsv
    #   (yyyy)-(s)-(pre/post)-anime.tsv
    #   (yyyy)-(s)-(pre/post)-lateadds.tsv
    # e.g. 2020-3-post.tsv for the post-summer 2020 survey

    file_name_list = [file_name for file_name in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file_name))]
    file_name_list.sort()
    
    while len(file_name_list) >= 2:
        match_list = re.findall(r'^(\d{4})-([0123])-(pre|post)-anime\.tsv', file_name_list[0])
        if match_list:
            group_list = match_list[0] # Should only be 1 match, but multiple groups
            year = int(group_list[0])
            quarter = int(group_list[1])
            is_preseason = group_list[2] == 'pre'

            survey_anime_file_path = os.path.join(folder_path, file_name_list[0])
            if len(file_name_list) >= 3 and file_name_list[1] == '%s-%s-%s-lateadds.tsv' % group_list:
                survey_late_adds_file_path = os.path.join(folder_path, file_name_list[1])
                survey_file_path = os.path.join(folder_path, file_name_list[2])
                file_name_list = file_name_list[3:]
            else:
                survey_late_adds_file_path = None
                survey_file_path = os.path.join(folder_path, file_name_list[1])
                file_name_list = file_name_list[2:]
            
            print('Found survey %i Q%i %s' % (year, quarter+1, 'pre' if is_preseason else 'post'))

            add_survey(survey_file_path, survey_anime_file_path, survey_late_adds_file_path, year, quarter, is_preseason)
        else:
            print('Could not match file: %s' % file_name_list[0])
            file_name_list = file_name_list[1:]
    
    if file_name_list:
        print('Could not import these files:', file_name_list)




def get_anime_by_id():
    answer = input('- Please type in an Anime ID or "N" to cancel')
    if answer.isdigit():
        try:
            anime = Anime.objects.get(id=int(answer))
        except:
            return get_anime_by_id()

        answer = input('- Is "%s" correct? (Y/N)' % str(anime))
        if answer.lower() == 'y':
            return anime
        else:
            return get_anime_by_id()

    elif answer.lower() == 'n':
        return None

    else:
        return get_anime_by_id()

DEBUG = False
def find_accompanying_anime(animename_str_list, is_series):
    animename_str_list = [animename_str.strip() for animename_str in animename_str_list]
    animename_str_list = [(animename_str if animename_str.find('(') < 0 else animename_str[:animename_str.find('(')].strip()) for animename_str in animename_str_list]

    print('Finding accompanying anime for %s' % str(animename_str_list))
    queryset_filter = Q(name__startswith=animename_str_list[0])
    for animename in animename_str_list[1:]:
        queryset_filter = queryset_filter | Q(name__startswith=animename)
    
    
    anime_series_filter = Q(anime__anime_type=Anime.AnimeType.TV_SERIES) | Q(anime__anime_type=Anime.AnimeType.ONA_SERIES) | Q(anime__anime_type=Anime.AnimeType.BULK_RELEASE)
    special_anime_filter = ~anime_series_filter
    if is_series:
        queryset_filter = queryset_filter & anime_series_filter
    else:
        queryset_filter = queryset_filter & special_anime_filter

    animename_queryset = AnimeName.objects.filter(queryset_filter)
    anime_list = [i[0] for i in animename_queryset.values_list('anime')]
    anime_list = sorted(list(set(anime_list)))
    anime_list = [Anime.objects.get(id=id) for id in anime_list]
    if DEBUG:
        anime_list = anime_list[:1]



    if len(anime_list) == 1:
        print('- Found "%s"' % anime_list[0])
        return anime_list[0]

    elif len(anime_list) > 1:
        print('- Multiple matching anime found! Please pick one (or type "N" to search for an Anime by ID):')
        for i in range(len(anime_list)):
            print('- %i: %s' % (i, str(anime_list[i])))

        answer = input()
        if answer.isdigit():
            answer = int(answer)
            print('- Selected "%s"' % anime_list[answer])
            return anime_list[answer]
        else:
            return get_anime_by_id()

    else:
        print('- No matching anime found!')
        return get_anime_by_id()

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

def add_survey(survey_file_path, survey_anime_file_path, survey_late_adds_file_path, year, quarter, is_preseason):
    survey_queryset = Survey.objects.filter(year=year, season=quarter, is_preseason=is_preseason)
    if len(survey_queryset) > 0:
        survey = survey_queryset[0]
        print('Found pre-existing survey: "%s"' % str(survey))

        answer = input('Delete this survey and continue? (Y/N)').lower()
        while answer != 'y' and answer != 'n':
            answer = input('Delete this survey and continue? (Y/N)').lower()
        
        if answer == 'n':
            return

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
            anime_series = find_accompanying_anime(series_str.split(' | '), True)
            anime_series_map[series_str] = anime_series
        
        special_str = split[1].strip()
        if special_str and not special_str.isspace():
            special_anime = find_accompanying_anime(special_str.split(' | '), False)
            special_anime_map[special_str] = special_anime

    
    # +---------------+
    # | GET LATE ADDS |
    # +---------------+
    if survey_late_adds_file_path:
        print('Reading late adds')
        fl = open(survey_late_adds_file_path, 'r', encoding='utf8')
        fl.readline()

        for line in fl:
            split = line.split('\t')
            anime_str_maybe = split[0].strip()
            add_response_count_str_maybe = split[1].strip()
            search_int = re.search(r'\d+', add_response_count_str_maybe)

            if search_int:
                add_response_count = int(search_int.group())
                if anime_str_maybe in anime_series_map.keys():
                    anime = anime_series_map[anime_str_maybe]
                elif anime_str_maybe in special_anime_map.keys():
                    anime = special_anime_map[anime_str_maybe]
                else:
                    continue
                
                if not anime:
                    continue

                sar = SurveyAdditionRemoval(
                    anime=anime,
                    is_addition=True,
                    response_count=add_response_count,
                    survey=survey,
                )
                sar.save()
                print('Found late add: "%s" added at %i responses' % (str(anime), add_response_count))

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
            header = headers[header_idx].strip()

            start = header.index('[')
            end = header.rindex(']')
            anime_str = header[start+1:end].strip()
            anime = anime_series_map[anime_str]

            anime_score_str = split[header_idx].strip()
            if anime and anime_score_str and not anime_score_str.isspace() and anime_score_str != 'N/A':
                anime_score = int(anime_score_str[0])
                animeresponse_map[anime].score = anime_score

            header_idx += 1
        
        # Get surprises/disappointments
        while headers[header_idx].startswith('What are your '):
            header = headers[header_idx].strip()

            start = header.index('[')
            end = header.rindex(']')
            anime_str = header[start+1:end].strip()
            anime = anime_series_map[anime_str]

            expectations_str = split[header_idx].strip()
            if anime and expectations_str and not expectations_str.isspace() and expectations_str != 'N/A':
                expectations = AnimeResponse.Expectations.SURPRISE if expectations_str == 'Surprise' else AnimeResponse.Expectations.DISAPPOINTMENT
                animeresponse_map[anime].expectations = expectations
            
            header_idx += 1
        

        # Get watching special anime
        watching_special_anime_str = split[header_idx]
        watching_special_anime_list = parse_anime_strlist(watching_special_anime_str, special_anime_map)
        for anime in watching_special_anime_list:
            animeresponse_map[anime].watching = True
        
        header_idx += 1

        # Get special anime scores
        while header_idx < len(headers) and headers[header_idx].startswith('How good '):
            header = headers[header_idx].strip()

            start = header.index('[')
            end = header.rindex(']')
            anime_str = header[start+1:end].strip()
            anime = special_anime_map[anime_str]

            anime_score_str = split[header_idx].strip()
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

