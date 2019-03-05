import re

# temporarily copied from botocore

_xform_cache = {
    ('CreateCachediSCSIVolume', '_'): 'create_cached_iscsi_volume',
    ('CreateCachediSCSIVolume', '-'): 'create-cached-iscsi-volume',
    ('DescribeCachediSCSIVolumes', '_'): 'describe_cached_iscsi_volumes',
    ('DescribeCachediSCSIVolumes', '-'): 'describe-cached-iscsi-volumes',
    ('DescribeStorediSCSIVolumes', '_'): 'describe_stored_iscsi_volumes',
    ('DescribeStorediSCSIVolumes', '-'): 'describe-stored-iscsi-volumes',
    ('CreateStorediSCSIVolume', '_'): 'create_stored_iscsi_volume',
    ('CreateStorediSCSIVolume', '-'): 'create-stored-iscsi-volume',
    ('ListHITsForQualificationType', '_'): 'list_hits_for_qualification_type',
    ('ListHITsForQualificationType', '-'): 'list-hits-for-qualification-type',
}
_first_cap_regex = re.compile('(.)([A-Z][a-z]+)')
_end_cap_regex = re.compile('([a-z0-9])([A-Z])')
_special_case_transform = re.compile('[A-Z]{3,}s$')


def xform_name(name, sep='_', _xform_cache=_xform_cache):
    """Convert camel case to a "pythonic" name.
    If the name contains the ``sep`` character, then it is
    returned unchanged.
    """
    if sep in name:
        # If the sep is in the name, assume that it's already
        # transformed and return the string unchanged.
        return name
    key = (name, sep)
    if key not in _xform_cache:
        if _special_case_transform.search(name) is not None:
            is_special = _special_case_transform.search(name)
            matched = is_special.group()
            # Replace something like ARNs, ACLs with _arns, _acls.
            name = name[:-len(matched)] + sep + matched.lower()
        s1 = _first_cap_regex.sub(r'\1' + sep + r'\2', name)
        transformed = _end_cap_regex.sub(r'\1' + sep + r'\2', s1).lower()
        _xform_cache[key] = transformed
    return _xform_cache[key]
