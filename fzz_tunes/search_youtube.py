# from youtubesearchpython import CustomSearch, VideoSortOrder
from youtubesearchpython import VideosSearch, VideoSortOrder


class SearchResult:
    def __init__(self, title, duration, link):
        self.title = title
        self.duration = duration
        self.link = link


class SearchYoutube:
    prevPage = []

    def search(self, textToSerach: str) -> list[SearchResult]:
        srch = VideosSearch(textToSerach)
        self.srch = srch
        search_results = self.srch.result()
        # Assuming serach_results contains the API response

        results_list = []
        for item in search_results['result']:
            result_instance = SearchResult(
                title=item['title'],
                duration=item['duration'],
                link=item['link']
            )
            results_list.append(result_instance)

        return results_list

    def nextPage(self):
        self.srch.next();
        return self.srch.result()
