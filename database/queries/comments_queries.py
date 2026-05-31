class CommentsQueries:
    INSERT = """
            INSERT INTO wp_comments(
            comment_post_id, comment_author, comment_date, comment_date_gmt,
            comment_content, comment_approved, user_id
            ) VALUES (
            %s, %s, NOW(), NOW(), %s, %s, %s
            )
            """
    DELETE = 'DELETE FROM wp_comments WHERE comment_ID = %s'
