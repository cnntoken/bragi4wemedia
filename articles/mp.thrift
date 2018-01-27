namespace py mp

typedef i32 int

struct Response {
1: required bool status,
2: required string reason,
3: optional string data,
}

service MPArticleProcessService
{
    void ping(),
    Response check_usable_status(1:string article_json_data, 2:string lang),
    Response create_article(1:string article_json_data),
    Response create_partner_article(1:string source_url, 2:string domain, 3:string title, 4:string content, 5:list<string> images, 6: string published_time),
    Response update_article_status(1:string source_url, 2:bool usable),
    Response sync_media_account(1:string site_url, 2:string site_name, 3:string media_icon, 4:int valid_duration),
    Response article_insert_slot(1:string source_url),
    Response batch_check_usable_status(1:string articles_json_data, 2:string lang),
}
