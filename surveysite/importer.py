from survey.models import Anime

def perform(file_path):
    f = open(file_path, 'r', encoding='utf8')
    f.readline()

    anime_list = []

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
            japanese_name=split[0],
            english_name=split[1],
            short_name='',
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

        if len(anime_list) >= 900: # SQLite can only handle a max of 999 variables per query
            Anime.objects.bulk_create(anime_list)
            anime_list.clear()
    
    if len(anime_list) > 0:
        Anime.objects.bulk_create(anime_list)
