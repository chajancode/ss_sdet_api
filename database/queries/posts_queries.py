class PostsQueries:
    INSERT = """
        INSERT INTO wp_posts(
        post_author, post_date, post_date_gmt, post_content, post_title,
        post_excerpt, post_status, post_name, to_ping, pinged, post_modified,
        post_modified_gmt, post_content_filtered, post_type
        ) VALUES (
        %s, NOW(), NOW(), %s, %s, '', %s, %s, '', '', NOW(), NOW(), '', %s
        )
        """

    DELETE = "DELETE FROM wp_posts WHERE ID = %s"
