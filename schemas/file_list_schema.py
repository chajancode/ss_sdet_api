file_list_schema = {
    'type': 'object',
    'required': ['items', 'limit'],
    'properties': {
        'limit': {'type': 'integer'},
        'offset': {'type': 'integer'},
        'items': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'path': {'type': 'string'},
                    'type': {'type': 'string'},
                    'name': {'type': 'string'},
                    'created': {'type': 'string', 'format': 'date-time'},
                    'modified': {'type': 'string', 'format': 'date-time'},
                    'size': {'type': 'integer'},
                    'mime_type': {'type': 'string'},
                    'md5': {'type': 'string'},
                    'sha256': {'type': 'string'},
                    'public_key': {'type': 'string'},
                    'public_url': {'type': 'string'},
                    'media_type': {'type': 'string'},
                    'resource_id': {'type': 'string'},
                    'revision': {'type': 'integer'},
                    'comment_ids': {
                        'type': 'object',
                        'properties': {
                            'public_resource': {'type': 'string'},
                            'private_resource': {'type': 'string'}
                        },
                    },
                    'exif': {},
                    'antivirus_status': {'type': 'string'},
                    'file': {'type': 'string'},
                }
            }
        }
    }
}
