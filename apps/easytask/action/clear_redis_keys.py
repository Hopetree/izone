from django.core.cache import cache


def action_clear_cache_with_prefix(pattern_keys):
    """
    清理指定匹配规则的redis keys
    @param pattern_keys:
    @return:
    """
    result = []
    keys_matching_pattern = cache.keys(pattern_keys)
    if keys_matching_pattern:
        for key in keys_matching_pattern:
            result.append(key)
            cache.delete(key)
    return result
