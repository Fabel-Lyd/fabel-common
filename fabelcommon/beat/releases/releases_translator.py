from typing import Dict, List


class ReleasesTranslator:

    @staticmethod
    def translate_releases(releases: List[Dict]):
        return [ReleasesTranslator._translate_release(release) for release in releases]

    @staticmethod
    def _translate_release(release: Dict):
        return {
            'isbn': release['ids']['isbn'],
            'title': release['title']
        }
