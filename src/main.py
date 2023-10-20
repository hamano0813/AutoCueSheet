import os
import sys
import re
from mutagen.flac import FLAC


def chinese_spacing(chinese: str, spacing: int = 120, blank: str = '-'):
    return chinese + ' ' + blank * (spacing - len(chinese) - len(re.findall('[^\x00-\u2dff]', chinese)) - 2) + ' '

def update_performer(cue_sheet: str, track: str, artists: list):
    track_num = re.findall('\d{2,3}', track)[0]
    track_partten = f'TRACK {track_num} AUDIO\n    TITLE .+'
    track_text = re.findall(track_partten, cue_sheet)
    if not track_text:
        return cue_sheet
    return cue_sheet.replace(track_text[0], f'{track_text[0]}\n    PERFORMER "{";".join(artists)}"')

def complete_performer(cue_sheet: str, album_artist: str):
    track_partten = 'TRACK \d{2,3} AUDIO\n    TITLE .+\n    INDEX'
    track_texts: list[str] = re.findall(track_partten, cue_sheet)
    for track_text in track_texts:
        texts = track_text.splitlines()
        texts.insert(2, f'    PERFORMER "{album_artist}"')
        cue_sheet = cue_sheet.replace(track_text, '\n'.join(texts))
    return cue_sheet

def id3_to_cue(flac_path: str) -> bool:
    path, ext = os.path.splitext(flac_path)
    if not ext.lower() == '.flac':
        print(f'{chinese_spacing(flac_path)}❎ failed! not flac!')
        return False

    file_name: str = os.path.split(flac_path)[-1]
    cue_path: str = path + '.cue'
    flac_audio: FLAC = FLAC(flac_path)

    cue_sheet: str = flac_audio['cuesheet'][0] if flac_audio['cuesheet'] else ''
    if not cue_sheet:
        print(f'{chinese_spacing(flac_path)}❎ failed! not cuesheet tag!')
        return False

    album_artist: str = flac_audio['albumartist'][0] if flac_audio[
        'albumartist'] else flac_audio['artist'][0]
    if not album_artist:
        print(f'{chinese_spacing(flac_path)}❎ failed! no artist info!')

    performer = f'\n    PERFORMER "{album_artist}"'
    cue_sheet = cue_sheet.replace('\r\n', '\n')
    cue_sheet = re.sub('"CDImage\.\w+"', f'"{file_name}"', cue_sheet)
    cue_sheet = cue_sheet.replace(performer, '')

    flac_keys = list(flac_audio.keys())
    for flac_key in flac_keys:
        if re.fullmatch('cue_track\d{2,3}_artist', flac_key):
            cue_sheet = update_performer(cue_sheet, flac_key, flac_audio[flac_key])

    cue_sheet = complete_performer(cue_sheet, album_artist)

    with open(cue_path, 'w', encoding='utf8') as f:
        f.write(cue_sheet.strip())
    print(f'{chinese_spacing(flac_path)}✅ done! 💯🎉🎉🎉')
    return True


if __name__ == '__main__':
    file_list = sys.argv[1:]
    count = 0
    if not file_list:
        input('Please drag the file to the program to convert the cue file!')
        exit(0)
    for file_path in file_list:
        count += id3_to_cue(file_path)
    input(f'\n{count} file is done!')
