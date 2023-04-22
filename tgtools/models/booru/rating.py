class RATING:
    """
    A utility class for handling generic Booru rating levels and their corresponding strings.

    Attributes:
        general (str): The general rating string.
        sensitive (str): The sensitive rating string.
        questionable (str): The questionable rating string.
        explicit (str): The explicit rating string.
        levels (dict[str, int]): A dictionary mapping rating strings to their corresponding integer levels.
        full_name_map (dict[str, str]): A dictionary mapping rating all variations of
                                        rating strings to their full name.
    """

    general = "rating:general"
    sensitive = "rating:sensitive"
    questionable = "rating:questionable"
    explicit = "rating:explicit"

    levels = {
        "rating:general": 0,
        "rating:sensitive": 1,
        "rating:questionable": 2,
        "rating:explicit": 3,
    }

    full_name_map = {
        "g": general,
        "general": general,
        "rating:general": general,
        "s": sensitive,
        "sensitive": sensitive,
        "rating:sensitive": sensitive,
        "q": questionable,
        "questionable": questionable,
        "rating:questionable": questionable,
        "e": explicit,
        "explicit": explicit,
        "rating:explicit": explicit,
    }

    @staticmethod
    def level(rating: str) -> int:
        """
        Get the integer level of a given rating.

        Args:
            rating (str): The rating string.

        Returns:
            int: The corresponding integer level of the rating.

        Examples:
            >>> RATING.level("g")
            0

            >>> RATING.level("sensitive")
            1

            >>> RATING.level("rating:explicit")
            3
        """
        return RATING.levels[RATING.full(rating)]

    @staticmethod
    def simple(rating: str) -> str:
        """
        Get the simple rating string from a given rating.

        Without the "rating:" part.

        Args:
            rating (str): The rating string.

        Returns:
            str: The simple rating string.

        Examples:
            >>> RATING.simple("g")
            "general"

            >>> RATING.simple("e")
            "explicit"
        """
        return RATING.full(rating).split(":")[-1]

    @staticmethod
    def full(rating: str) -> str:
        """
        Get the full rating string from a given rating.

        Args:
            rating (str): The rating string.

        Returns:
            str: The full rating string.

        Examples:
            >>> RATING.simple("g")
            "rating:general"

            >>> RATING.simple("rating:sensitive")
            "rating:sensitive"

            >>> RATING.simple("explicit")
            "rating:explicit"
        """
        return RATING.full_name_map[rating]
