namespace py mp

typedef i32 int

struct Response{
1: required bool status,
2: required string reason,
3: optional string data,
}

service MPCommentProcessService
{
    string ping(),
    Response get_unread_comments_count(1:map<string, string> media_infos),
    Response get_comments(1:string site_url, 2:string site_name, 3:int count),
    Response reply_comment(1:int article_seq_id, 2:string reply_to, 3:string content, 4:string reply_user_info_json, 5:string reply_comment_id, 6:string reply_comment_content, 7:string media_online_site_url),
    Response get_comments_by_article(1:int article_seq_id, 2:string read_tag, 3:int count, 4:string action),
    Response get_comments_count_by_article(1:list<string> article_seq_ids_json),
}
