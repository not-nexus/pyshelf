from pyshelf.search.sort_type import SortType
from pyshelf.search.sort_flag import SortFlag
from pyshelf.search.type import Type as SearchType
import re


class SearchParser(object):
    def from_request(self, request_criteria):
        """
            Turns the given request into search criteria that can be consumed by pyshelf.search module.

            Args:
                request_criteria(dict): Search and sort criteria from the request.

            Returns:
                dict: search and sort criteria that will be consumed by search layer
        """
        search_criteria = []
        sort_criteria = []

        for search in request_criteria["search"]:
            search_criteria.append(self._format_search_criteria(search))

        if request_criteria.get("sort"):
            for sort in request_criteria["sort"]:
                sort_criteria.append(self._format_sort_criteria(sort))

        formatted_criteria = {"search": search_criteria, "sort": sort_criteria}

        return formatted_criteria

    def _format_search_criteria(self, search_string):
        """
            Formats search criteria from search string

            Args:
                search_string(string): Search string from request, ex: "version~=1.1"

            Returns:
                dict: search criteria dictionary
        """
        search_criteria = {}
        # Both regex's match unless characters are escaped with \
        version_search = r"[^\\]\~"
        wildcard_search = r"[^\\]\*"
        split_char = "="

        # Finds first occurance of = and checks for unescaped tilde in substring
        index = search_string.find("=")
        sub_string = search_string[index - 2:index]

        if re.search(version_search, sub_string):
            search_criteria["search_type"] = SearchType.VERSION
            split_char = "~="
        else:
            if re.search(wildcard_search, search_string):
                search_criteria["search_type"] = SearchType.WILDCARD
            else:
                search_criteria["search_type"] = SearchType.MATCH

        search_criteria["field"], search_criteria["value"] = search_string.split(split_char, 1)
        return search_criteria

    def _format_sort_criteria(self, sort_string):
        """
            Formats sort criteria from sort string

            Args:
                sort_string(string): Sort string from request, ex: "version, VERSION, ASC"

            Returns:
                dict: sort criteria dictionary
        """
        sort_criteria = {}
        flag_list = []
        sort_list = sort_string.split(",")
        sort_criteria["field"] = sort_list.pop(0).strip()

        for sort_string in sort_list:
            sort_string = sort_string.strip()
            sort_type = SortType.get_alias(sort_string)
            sort_flag = SortFlag.get_alias(sort_string)

            if sort_type:
                sort_criteria["sort_type"] = sort_type
            elif sort_flag:
                flag_list.append(sort_flag)

        if flag_list:
            sort_criteria["flag_list"] = flag_list

        if not sort_criteria.get("sort_type"):
            sort_criteria["sort_type"] = SortType.ASC

        return sort_criteria
