# ShortFlow DB 스키마 (MySQL autoda)

> 최종 갱신: 2026-02-23 KST  
> DB: autoda | Host: localhost | User: pigupuser (읽기 전용 접근)

## 개요

- **DB명:** autoda
- **주요 용도:** 뉴톡 쇼핑몰 상품 DB (ShortFlow/StyleFlow 원본 데이터)
- **전체 테이블 수:** 226

## 테이블 요약

| TABLE_NAME | TABLE_ROWS | DATA_LENGTH | CREATE_TIME | UPDATE_TIME | 용도 |
|----------|-------|-------------|---------------------|---------------------|------|
| aauth_groups | 3 | 60 | 2021-12-31 21:52:19 | 2021-12-31 21:52:19 | |
| aauth_perms | 0 | 0 | 2021-12-31 21:52:19 | 2021-12-31 21:52:19 | |
| aauth_perm_to_group | 0 | 0 | 2021-12-31 21:52:19 | 2021-12-31 21:52:19 | |
| aauth_perm_to_user | 0 | 0 | 2021-12-31 21:52:19 | 2021-12-31 21:52:19 | |
| aauth_pms | 0 | 0 | 2021-12-31 21:52:19 | 2021-12-31 21:52:19 | |
| aauth_system_variables | 0 | 0 | 2021-12-31 21:52:19 | 2021-12-31 21:52:19 | |
| aauth_users | 1 | 124 | 2021-12-31 21:52:19 | 2021-12-31 21:52:19 | |
| aauth_user_to_group | 2 | 18 | 2021-12-31 21:52:19 | 2021-12-31 21:52:19 | |
| aauth_user_variables | 0 | 0 | 2021-12-31 21:52:19 | 2021-12-31 21:52:19 | |
| admin | 1 | 112 | 2021-12-31 21:52:19 | 2021-12-31 21:52:19 | |
| aligo_template | 50 | 21784 | 2021-12-31 21:52:19 | 2021-12-31 21:52:19 | |
| arrival | 931 | 26068 | 2023-01-16 17:01:30 | 2026-02-20 18:28:52 | |
| arrival_block | 1072 | 102516 | 2022-07-01 15:37:20 | 2026-02-20 18:28:52 | |
| arrival_block_new | 931 | 57292 | 2023-01-04 11:02:54 | 2026-02-20 18:28:12 | |
| auth_phone_number | 558 | 65536 | 2025-04-15 10:39:47 | 2026-02-22 09:40:47 | |
| banner | 4 | 672 | 2022-11-24 17:29:58 | 2024-09-06 10:54:34 | |
| banner_modify_logs | 79 | 5532 | 2022-11-22 15:47:39 | 2024-09-06 10:54:13 | |
| board | 0 | 0 | 2021-12-31 21:52:19 | 2021-12-31 21:52:19 | |
| board_ad | 0 | 0 | 2021-12-31 21:52:19 | 2021-12-31 21:52:19 | |
| board_ci | 0 | 0 | 2021-12-31 21:52:19 | 2021-12-31 21:52:19 | |
| board_ci_make | 0 | 0 | 2021-12-31 21:52:19 | 2021-12-31 21:52:19 | |
| board_etc_qna | 0 | 0 | 2021-12-31 21:52:19 | 2021-12-31 21:52:19 | |
| board_file | 0 | 0 | 2021-12-31 21:52:19 | 2021-12-31 21:52:19 | |
| board_free | 0 | 0 | 2021-12-31 21:52:19 | 2021-12-31 21:52:19 | |
| board_html5 | 0 | 0 | 2021-12-31 21:52:19 | 2021-12-31 21:52:19 | |
| board_job | 0 | 0 | 2021-12-31 21:52:19 | 2021-12-31 21:52:19 | |
| board_lecture | 0 | 0 | 2021-12-31 21:52:19 | 2021-12-31 21:52:19 | |
| board_list | 9 | 528 | 2021-12-31 21:52:19 | 2021-12-31 21:52:19 | |
| board_news | 0 | 0 | 2021-12-31 21:52:19 | 2021-12-31 21:52:19 | |
| board_notice | 0 | 0 | 2021-12-31 21:52:19 | 2021-12-31 21:52:19 | |
| board_qna | 0 | 0 | 2021-12-31 21:52:19 | 2021-12-31 21:52:19 | |
| board_source | 0 | 0 | 2021-12-31 21:52:19 | 2021-12-31 21:52:19 | |
| board_su | 0 | 0 | 2021-12-31 21:52:19 | 2021-12-31 21:52:19 | |
| board_tip | 0 | 0 | 2021-12-31 21:52:19 | 2021-12-31 21:52:19 | |
| building_info | 41 | 16384 | 2022-09-22 15:15:35 | NULL | |
| building_sector_info | 20207 | 2621440 | 2022-04-21 13:37:32 | NULL | |
| cafe24_logs | 14 | 2912 | 2021-12-31 21:52:19 | 2021-12-31 21:52:19 | |
| cafe24_settigs | 354 | 129760 | 2021-12-31 21:52:19 | 2025-12-20 14:58:42 | |
| cafe24_status | 341712 | 2948331512 | 2021-12-31 21:52:19 | 2025-12-20 14:59:29 | |
| cafe24_token | 400 | 54992 | 2021-12-31 21:53:31 | 2026-01-08 11:18:39 | |
| ci_sessions | 2 | 336 | 2021-12-31 21:53:31 | 2021-12-31 21:53:31 | |
| cjapi_token | 324 | 65536 | 2023-03-27 17:57:07 | 2026-02-19 14:27:13 | |
| click | 0 | 0 | 2021-12-31 21:53:31 | 2021-12-31 21:53:31 | |
| codyImg_msg | 5706 | 493524 | 2024-10-08 17:43:06 | 2026-02-20 17:35:17 | |
| cody_msg | 5702 | 1009108 | 2024-12-18 12:07:35 | 2026-02-20 17:35:17 | 코디 메시지 |
| cody_product_msg | 8067 | 2120720 | 2025-01-07 16:38:12 | 2026-02-23 16:06:26 | 코디-상품 매핑 |
| company_groups | 23802 | 404634 | 2021-12-31 21:53:31 | 2024-01-26 10:55:51 | |
| contents_msg | 506 | 94496 | 2024-05-06 12:25:57 | 2026-02-20 17:35:17 | |
| coupon_generate | 0 | 16384 | 2022-08-22 15:31:28 | NULL | |
| coupon_setting | 0 | 16384 | 2022-10-24 17:11:33 | NULL | |
| coupon_used | 0 | 16384 | 2022-06-22 23:48:16 | NULL | |
| cron_reserve | 3 | 132 | 2021-12-31 21:53:31 | 2021-12-31 21:53:31 | |
| cron_reserve_goods | 11 | 220 | 2021-12-31 21:53:31 | 2021-12-31 21:53:31 | |
| cron_status | 109087 | 345601020 | 2021-12-31 21:53:31 | 2026-01-24 09:00:34 | |
| customer | 2 | 16384 | 2021-12-31 21:53:33 | NULL | |
| custom_push_msg | 1 | 276 | 2023-01-25 16:22:17 | 2023-09-13 11:18:04 | |
| custom_push_msg_logs | 5 | 95 | 2023-01-25 16:30:14 | 2023-09-12 10:34:55 | |
| delivery_info | 3 | 16384 | 2021-12-31 21:53:33 | NULL | |
| delivery_kind_logs | 0 | 0 | 2022-05-24 18:44:25 | 2022-05-24 18:44:25 | |
| delivery_package_logs | 0 | 0 | 2022-05-24 18:44:55 | 2022-05-24 18:44:55 | |
| delivery_package_price | 120 | 3480 | 2022-09-22 15:18:46 | 2022-11-29 14:51:52 | |
| deposit_refund | 90 | 7684 | 2022-03-10 15:07:57 | 2025-11-19 09:51:22 | |
| device_info | 40493 | 9977856 | 2021-12-31 21:53:33 | 2026-02-23 15:12:55 | |
| device_info_new | 0 | 16384 | 2021-12-31 21:53:33 | NULL | |
| excel_data_result_log | 54 | 16160 | 2022-04-21 15:20:58 | 2022-04-28 14:15:24 | |
| faq_category | 5 | 908 | 2022-11-07 14:24:53 | 2022-11-15 16:08:12 | |
| faq_category_modify_logs | 521 | 38476 | 2022-10-17 11:03:43 | 2022-11-15 16:08:12 | |
| faq_qa | 7 | 21516 | 2022-10-18 15:53:18 | 2023-05-19 00:15:33 | |
| faq_qa_modify_logs | 242 | 64760 | 2022-07-21 15:32:32 | 2023-05-19 00:17:44 | |
| files | 0 | 0 | 2021-12-31 21:53:33 | 2021-12-31 21:53:33 | |
| goods | 77122 | 103059616 | 2026-02-09 23:59:58 | 2026-02-23 17:08:43 | ShortFlow 영상 소스(상품 마스터) |
| goods_20230830 | 53747 | 88719360 | 2023-08-30 17:18:44 | NULL | |
| goods_20260106 | 76603 | 102090620 | 2026-01-06 16:20:18 | 2026-01-06 16:20:19 | |
| goods_action_logs | 1042912 | 41066796 | 2021-12-31 21:53:37 | 2026-02-23 17:27:58 | |
| goods_banner | 1386 | 95764 | 2021-12-31 21:53:38 | 2026-02-13 17:28:03 | |
| goods_best | 15832 | 697380 | 2021-12-31 21:53:38 | 2026-02-23 00:03:47 | |
| goods_biz_logs | 157071 | 6246552 | 2021-12-31 21:53:38 | 2026-02-23 16:50:32 | |
| goods_cafe24 | 334455 | 62887528 | 2022-10-07 13:43:08 | 2025-12-20 14:59:32 | |
| goods_cate | 33520 | 3393448 | 2023-02-08 10:51:21 | 2023-02-08 13:47:22 | |
| goods_code | 78051 | 2833096 | 2021-12-31 21:53:42 | 2026-02-23 17:27:58 | |
| goods_code_image_compress_log | 485015 | 51083276 | 2024-04-12 19:19:52 | 2026-02-23 17:27:21 | |
| goods_color_list | 139 | 5660 | 2022-09-06 11:20:07 | 2026-01-27 15:59:10 | |
| goods_cron | 21470 | 5083196 | 2021-12-31 21:53:43 | 2021-12-31 21:53:44 | |
| goods_detail | 77128 | 1068689064 | 2024-04-12 21:14:40 | 2026-02-23 17:08:43 | |
| goods_detail_backup_* | (백업 테이블 다수) | | | | |
| goods_detail_cron | 21470 | 63035268 | 2021-12-31 21:53:57 | 2021-12-31 21:53:59 | |
| goods_down | 333826 | 17291976 | 2021-12-31 21:53:59 | 2026-02-23 15:15:04 | |
| goods_down_status | 1992094 | 82803628 | 2021-12-31 21:54:00 | 2026-02-23 16:38:28 | |
| goods_excel | 953 | 105640 | 2021-12-31 21:54:12 | 2021-12-31 21:54:12 | |
| goods_excel_new | 1618 | 731324 | 2021-12-31 21:54:12 | 2024-06-25 14:20:37 | |
| goods_fit_list | 22 | 988 | 2022-09-06 15:51:59 | 2022-09-06 15:52:12 | |
| goods_image | 76905 | 26339940 | 2024-04-12 21:17:30 | 2026-02-23 16:01:05 | |
| goods_image_compress_log | 28711 | 2453908 | 2024-04-12 19:18:47 | 2024-04-12 19:18:47 | |
| goods_image_cron | 21470 | 9643500 | 2021-12-31 21:54:13 | 2021-12-31 21:54:13 | |
| goods_image_down_price | 6 | 16384 | 2024-07-02 09:57:14 | NULL | |
| goods_image_save_log | 481560 | 49532812 | 2021-12-31 21:54:13 | 2022-01-01 11:45:15 | |
| goods_master | 87646 | 12735984 | 2024-04-15 18:34:15 | 2026-02-23 15:25:30 | |
| goods_model_info | 33 | 1928 | 2023-02-07 17:18:41 | 2024-03-05 11:26:13 | |
| goods_model_modify_logs | 72 | 2736 | 2022-09-08 17:31:01 | 2022-09-08 17:33:07 | |
| goods_ocean | 1526880 | 155188292 | 2023-12-07 11:41:51 | 2026-02-23 16:48:01 | |
| goods_only_logs | 13408 | 582952 | 2021-12-31 21:54:22 | 2025-11-05 15:13:18 | |
| goods_option_code | 129226 | 6292668 | 2022-05-03 17:21:57 | 2026-02-23 16:01:05 | |
| goods_option_etc | 55 | 2376 | 2022-09-07 13:47:42 | 2023-08-30 16:56:06 | |
| goods_option_modify_logs | 0 | 0 | 2022-09-06 17:38:34 | 2022-09-06 17:38:34 | |
| goods_sample | 0 | 16384 | 2023-08-11 12:51:21 | NULL | |
| goods_size_info | 32 | 7596 | 2022-08-29 16:15:48 | 2025-03-06 18:33:37 | |
| goods_size_modify_logs | 37 | 5172 | 2022-08-24 17:07:16 | 2023-02-27 16:58:18 | |
| goods_watermark_* | (워터마크 관련 테이블 다수) | | | | |
| goods_wholesale_contract | 43467 | 3758572 | 2024-10-29 17:07:08 | 2026-02-23 17:08:43 | |
| goods_wish | 334640 | 14686044 | 2021-12-31 21:54:28 | 2026-02-23 15:13:40 | |
| groups_name | 83 | 3012 | 2021-12-31 21:54:30 | 2024-01-26 10:29:13 | |
| kakao_template_list_for_message | 0 | 16384 | 2021-12-31 21:54:30 | NULL | |
| login_attempts | 77 | 4528 | 2021-12-31 21:54:30 | 2026-02-23 14:49:10 | |
| mall_popup | 2 | 160 | 2021-12-31 21:54:30 | 2021-12-31 21:54:30 | |
| market_goods_cate | 2 | 1578664 | 2021-12-31 21:54:30 | 2021-12-31 21:54:30 | |
| market_goods_gosi | 50 | 114024 | 2021-12-31 21:54:30 | 2021-12-31 21:54:30 | |
| message | 5862 | 4027920 | 2021-12-31 21:54:30 | 2021-12-31 21:54:31 | |
| newtalk_template_msg | 4 | 32768 | 2022-03-11 14:33:51 | NULL | |
| notice | 18 | 59164 | 2022-10-04 13:21:18 | 2024-01-25 15:06:47 | |
| notice_category | 2 | 76 | 2022-08-23 11:45:36 | 2022-08-23 13:23:47 | |
| notice_category_modify_logs | 0 | 0 | 2022-08-23 11:52:49 | 2022-08-23 11:52:49 | |
| notice_modify_logs | 244 | 139148 | 2022-08-24 10:56:16 | 2024-01-25 15:06:47 | |
| NPLUS | 18046 | 7987464 | 2021-12-31 21:52:19 | 2024-02-07 03:07:11 | |
| nt_name_mapping_* | (이름 매핑 테이블) | | | | |
| nt_name_pool | 143 | 16384 | 2026-02-11 22:27:36 | 2026-02-11 22:27:57 | |
| ordered_items | 2 | 16384 | 2021-12-31 21:54:31 | NULL | |
| orders | 779 | 24928 | 2023-01-16 17:18:47 | 2026-02-22 18:44:39 | |
| orders_old | 0 | 16384 | 2023-01-04 10:51:06 | NULL | |
| order_barcode | 386885 | 58947408 | 2024-11-04 10:51:03 | 2026-02-23 12:33:33 | |
| order_barcode_upload | 3790 | 191356 | 2022-04-29 16:31:26 | 2026-02-23 10:32:01 | |
| order_block | 936 | 138776 | 2025-02-11 17:06:33 | 2026-02-22 18:44:39 | |
| order_block_alimTalk_logs | 926 | 19446 | 2022-05-20 16:43:44 | 2026-02-22 18:44:49 | |
| order_block_detail | 494790 | 131891496 | 2025-02-11 17:15:42 | 2026-02-23 05:19:40 | |
| order_block_modify_logs | 14 | 504 | 2022-04-21 13:21:34 | 2022-06-24 13:48:10 | |
| order_block_new | 831 | 51616 | 2023-01-04 10:48:01 | 2026-02-22 18:44:04 | |
| order_norelease_modify_logs | 56388 | 4559128 | 2022-06-13 13:53:55 | 2026-02-23 05:19:40 | |
| order_product | 368841 | 69958676 | 2023-01-04 11:42:16 | 2026-02-22 18:44:39 | |
| order_product_box | 70476 | 1057140 | 2023-01-05 15:50:37 | 2026-02-20 18:28:52 | |
| order_product_status | 377638 | 21117812 | 2023-01-04 11:53:18 | 2026-02-20 18:28:52 | |
| order_request | 88549 | 9889292 | 2023-06-30 15:53:30 | 2026-02-23 05:19:39 | |
| order_search_logs | 87 | 3892 | 2022-04-21 15:24:26 | 2023-12-24 23:22:58 | |
| order_store_check_logs | 78924 | 1815252 | 2022-07-06 16:57:16 | 2026-02-23 13:04:16 | |
| pickup_* | (픽업/배송 관련 테이블) | | | | |
| pigup_* | (피굽 주문/설정) | | | | |
| popup | 14 | 11924 | 2022-10-28 15:40:40 | 2024-01-25 15:17:45 | |
| push_reservation | 17 | 16384 | 2021-12-31 21:54:31 | NULL | |
| sabangnet_id_info | 479 | 18684 | 2021-12-31 21:54:31 | 2021-12-31 21:54:31 | |
| search_words | 0 | 0 | 2021-12-31 21:54:31 | 2021-12-31 21:54:31 | |
| shipping_address | 5 | 16384 | 2021-12-31 21:54:31 | NULL | |
| site_log | 5606204 | 1536163840 | 2025-05-19 17:28:14 | 2026-02-23 17:36:04 | |
| sns_send_template_msg | 5 | 1632 | 2022-09-30 15:57:49 | 2023-10-17 18:04:02 | |
| sns_template_logs | 15 | 1364 | 2022-09-30 16:06:35 | 2023-06-30 11:19:32 | |
| store_ftp_config | 5 | 392 | 2021-12-31 21:54:33 | 2021-12-31 21:54:33 | |
| tags | 0 | 0 | 2021-12-31 21:54:33 | 2021-12-31 21:54:33 | |
| temp_user_profiles | 24 | 2032 | 2021-12-31 21:54:33 | 2021-12-31 21:54:33 | |
| users | 79460 | 10495776 | 2026-02-10 00:16:54 | 2026-02-23 16:38:12 | |
| users_2024062705 | 76564 | 10087464 | 2024-06-28 13:41:33 | 2024-06-28 13:41:38 | |
| users_2109012314 | 5983 | 1128980 | 2021-12-31 21:54:33 | 2021-12-31 21:54:34 | |
| user_apikey | 4 | 236 | 2021-12-31 21:54:33 | 2024-06-15 15:37:13 | |
| user_autologin | 294 | 67120 | 2021-12-31 21:54:33 | 2024-05-28 18:59:15 | |
| user_client | 2 | 16384 | 2021-12-31 21:54:33 | NULL | |
| user_company_match | 36651 | 623084 | 2021-12-31 21:54:33 | 2025-11-17 10:28:12 | |
| user_delivery_partner | 16 | 2156 | 2021-12-31 21:54:33 | 2021-12-31 21:54:33 | |
| user_deposit | 104622 | 9617668 | 2023-11-10 18:11:18 | 2026-02-23 16:08:50 | |
| user_deposit_pg | 35 | 16384 | 2024-07-02 17:46:29 | NULL | |
| user_down_service | 2888 | 128984 | 2021-12-31 21:54:33 | 2026-02-07 11:15:20 | |
| user_employee | 6 | 16384 | 2021-12-31 21:54:33 | NULL | |
| user_freelancer | 33 | 6580 | 2024-10-15 11:52:42 | 2025-04-02 19:12:04 | |
| user_id_update_logs | 40 | 1700 | 2022-11-17 10:05:28 | 2025-03-05 17:53:38 | |
| user_login_log | 238227 | 10435300 | 2022-02-17 09:42:50 | 2026-02-23 16:35:36 | |
| user_manager | 48 | 3984 | 2023-11-30 16:13:21 | 2026-01-27 21:34:08 | |
| user_manual_log | 340 | 14960 | 2022-11-17 15:33:28 | 2024-01-24 17:50:23 | |
| user_market | 33 | 1488 | 2021-12-31 21:54:33 | 2021-12-31 21:54:33 | |
| user_market_info | 5 | 10252 | 2021-12-31 21:54:33 | 2021-12-31 21:54:33 | |
| user_model | 36 | 7596 | 2023-12-20 19:29:31 | 2026-01-28 16:58:09 | |
| user_msg | 1452615 | 607125504 | 2021-12-31 21:54:33 | 2026-02-22 18:45:38 | |
| user_msg_aligo | 71841 | 67715072 | 2023-11-10 11:37:45 | NULL | |
| user_partner | 25 | 16384 | 2021-12-31 21:54:33 | NULL | |
| user_partner_match | 96691 | 6799360 | 2022-11-24 14:22:19 | NULL | |
| user_pay | 0 | 0 | 2021-12-31 21:54:33 | 2021-12-31 21:54:33 | |
| user_place | 90 | 16528 | 2024-06-11 12:16:32 | 2026-02-13 15:05:53 | |
| user_popup_list | 9679 | 251654 | 2022-05-30 12:05:23 | 2026-02-23 14:52:37 | |
| user_profiles | 79415 | 13874116 | 2024-01-03 11:12:55 | 2026-02-22 18:44:23 | |
| user_profiles_2109012314 | 5961 | 1353268 | 2021-12-31 21:54:33 | 2021-12-31 21:54:33 | |
| user_qna_group | 868 | 65536 | 2021-12-31 21:54:33 | NULL | |
| user_qna_msg | 299 | 65536 | 2021-12-31 21:54:33 | NULL | |
| user_sns | 8 | 504 | 2021-12-31 21:54:33 | 2021-12-31 21:54:33 | |
| user_store_bookmark | 15 | 540 | 2021-12-31 21:54:33 | 2021-12-31 21:54:33 | |
| user_template_msg | 28 | 16384 | 2021-12-31 21:54:33 | NULL | |
| user_unregister_reason | 64 | 32768 | 2022-11-06 20:04:10 | 2026-02-16 15:48:50 | |
| user_wholesale_charge | 562 | 88600 | 2024-12-06 12:05:48 | 2026-02-12 12:46:23 | |
| user_wholesale_contract | 80 | 9012 | 2026-02-10 19:26:59 | 2026-02-10 19:51:24 | |
| user_wholesale_contract_history | 8 | 4584 | 2021-12-31 21:54:33 | 2023-09-06 08:15:33 | |
| user_wholeSale_log | 407 | 16384 | 2024-07-19 12:44:09 | 2026-02-04 15:33:56 | |
| use_end_day_history | 2403 | 57672 | 2021-12-31 21:54:33 | 2026-02-10 11:55:42 | |
| v1_status | 3229 | 320096 | 2021-12-31 21:54:34 | 2025-12-08 10:17:04 | |
| wholesale_billing_adjustment | 0 | 16384 | 2026-02-10 14:53:21 | NULL | |
| wholesale_billing_draft | 29 | 16384 | 2026-02-10 19:27:04 | 2026-02-10 21:32:35 | |
| wholesale_billing_log | 4 | 16384 | 2026-02-10 14:53:26 | 2026-02-10 20:14:16 | |

* 위 요약에서 일부 테이블은 그룹명으로 축약했으며, 전체 226개 테이블 목록·통계는 `docs/database/db_table_summary_md.txt` 또는 DB 덤프 스크립트로 확인 가능.

## 주요 테이블 상세

### goods (상품 마스터, ShortFlow 영상 소스)

| 컬럼명 | 타입 | Null | Key | Default | 설명 |
|--------|------|------|-----|---------|------|
| id | int(11) | NO | PRI | NULL | auto_increment |
| user_id | int(11) | NO | MUL | NULL | 회원 일련번호 |
| GdsMstId | int(11) | NO | MUL | 0 | 상품 마스터 일련번호 |
| market | char(1) | NO | MUL | NULL | 등록마켓 |
| Category1 | varchar(50) | NO | MUL | NULL | 대분류 |
| Category2 | varchar(50) | NO | MUL | NULL | 중분류 |
| Category3 | varchar(50) | NO | MUL | NULL | 소분류 |
| Category4 | varchar(50) | YES | | NULL | 세분류 |
| GoodsName | varchar(50) | YES | | NULL | 상품명 |
| GoodsCode | varchar(20) | NO | MUL | NULL | 상품코드(이미지 다운로드용) |
| BrandName | varchar(50) | NO | MUL | NULL | 브랜드 |
| GoodsPrice | int(10) unsigned | YES | | NULL | 판매가격 |
| GoodsImage | varchar(150) | YES | | NULL | 기본이미지 |
| activated | char(1) | NO | MUL | N | 상품노출제한(Y:노출,N:미노출) |
| created | datetime | YES | MUL | 0000-00-00 00:00:00 | 등록일 |
| modified | timestamp | YES | | current_timestamp() | on update |

* 기타 컬럼 100개 이상 (GoodsEtc*, 옵션, 워터마크, 업무진행 등) — 상세는 `SHOW CREATE TABLE goods` / `DESCRIBE goods` 참고.

- **행 수 (기준일):** 77,122

### cody_msg (코디 메시지)

| 컬럼명 | 타입 | Null | Key | Default | 설명 |
|--------|------|------|-----|---------|------|
| id | int(10) unsigned | NO | PRI | NULL | auto_increment, 코디일련번호 |
| codyCode | varchar(50) | YES | MUL | NULL | 코디코드 |
| shooting_id | int(10) | YES | MUL | NULL | 촬영ID(contents_msg.id) |
| mdMemo | varchar(50) | YES | | NULL | MD메모 |
| codyName | varchar(255) | YES | | NULL | 코디이름 |
| created | datetime | YES | | NULL | 생성일 |
| Model_shooting_complete_date | date | YES | | NULL | |
| codyNumber | int(50) | YES | | NULL | |

- **행 수 (기준일):** 5,702

### cody_product_msg (코디-상품 매핑)

| 컬럼명 | 타입 | Null | Key | Default | 설명 |
|--------|------|------|-----|---------|------|
| id | int(11) unsigned | NO | PRI | NULL | auto_increment |
| codyCode | varchar(255) | YES | | NULL | 코디코드(cody_msg.codyCode) |
| codyProdCode | varchar(255) | YES | MUL | NULL | 상품코드(goods.GoodsCode) |
| codyProdName | varchar(255) | YES | | NULL | 상품명 |
| codyProdColor | text | YES | | NULL | 상품색상 |
| codyProdSize | text | YES | | NULL | 상품사이즈 |
| codyProdNAS | text | YES | | NULL | NAS설정 |
| codyProdMemo | varchar(255) | YES | | NULL | MD메모 |
| created | datetime | YES | | NULL | 코디등록일 |
| useCody | int(11) | YES | | NULL | 촬영용/코디용 구분 |
| shooting_id | int(11) | YES | MUL | NULL | 촬영ID(contents_msg.id) |
| BizProgress | varchar(255) | YES | | E1 | 업무진행 상태 |
| WebWorker | varchar(255) | YES | | NULL | 웹디자이너 |
| TotalPriceWebworker | varchar(255) | YES | | NULL | 총금액(웹디자이너) |
| WebWorkerDate | date | YES | | NULL | 웹디자이너 할당일 |
| WebWorkerDoneDate | date | YES | | NULL | 웹작업 완료일 |
| WebWorkerMemo | varchar(50) | YES | | NULL | 웹디자이너 메모 |
| WebWorkerNAS | varchar(4000) | YES | | NULL | 편집완료NAS |
| Surcharge | varchar(255) | YES | | NULL | 기타 추가 금액 |
| SurchargeContent | varchar(255) | YES | | NULL | 기타 추가 금액 메모 |
| PaymentStatus | tinyint(2) | YES | | 1 | 정산상태 |
| GoodsEtc6 | varchar(50) | YES | | NULL | 도매처 |
| PaymentDate | date | YES | | NULL | 정산확인일 |
| PaymentDoneDate | date | YES | | NULL | 정산완료일 |

- **행 수 (기준일):** 8,067

## 전체 테이블 DESCRIBE

전체 226개 테이블에 대한 DESCRIBE 및 row_count 덤프는 작업 지시서 Step 1의 `db_all_tables.txt` 생성 스크립트로 재생성할 수 있다.  
문서화 시점 덤프는 `/tmp/db_all_tables.txt` (약 4,400줄) 형식으로 보관 가능.

## 인덱스 정보

### goods

| Key_name | Column_name | Non_unique | Index_type |
|----------|-------------|------------|------------|
| PRIMARY | id | 0 | BTREE |
| user_id | user_id | 1 | BTREE |
| market | market | 1 | BTREE |
| GdsMstId | GdsMstId | 1 | BTREE |
| SendCheck | SendCheck | 1 | BTREE |
| GoodsCode | GoodsCode | 1 | BTREE |
| activated | activated | 1 | BTREE |
| GoodsEtc6 | GoodsEtc6 | 1 | BTREE |
| GoodsEtc52 | GoodsEtc52 | 1 | BTREE |
| mall_activated | mall_activated | 1 | BTREE |
| activated_day | activated_day | 1 | BTREE |
| BrandName | BrandName | 1 | BTREE |
| Category1 | Category1 | 1 | BTREE |
| Category2 | Category2 | 1 | BTREE |
| Category3 | Category3 | 1 | BTREE |
| re_created | re_created | 1 | BTREE |
| idx_goods_stockingdate | StockingDate | 1 | BTREE |
| idx_goods_user_id_id | user_id, id | 1 | BTREE |
| idx_goods_user_activated_created | user_id, activated, created | 1 | BTREE |
| idx_goods_user_gdsmstid | user_id, GdsMstId | 1 | BTREE |
| idx_goods_user_sendcheck_id | user_id, SendCheck, id | 1 | BTREE |
| idx_goods_samplestage | SampleStage | 1 | BTREE |
| idx_goods_sample_created | SampleStage, created | 1 | BTREE |
| idx_goods_created | created | 1 | BTREE |

### cody_msg

| Key_name | Column_name | Non_unique | Index_type |
|----------|-------------|------------|------------|
| PRIMARY | id | 0 | BTREE |
| shooting_id | shooting_id | 1 | BTREE |
| codyCode | codyCode | 1 | BTREE |

### cody_product_msg

| Key_name | Column_name | Non_unique | Index_type |
|----------|-------------|------------|------------|
| PRIMARY | id | 0 | BTREE |
| codyProdCode | codyProdCode(250) | 1 | BTREE |
| shooting_id | shooting_id | 1 | BTREE |

## Supabase 테이블 (참고)

- **ShortFlow:** tenants, channels, products, jobs, analytics
- **StyleFlow:** sf_tenants, sf_brands, sf_channels, sf_videos, sf_upload_schedule

(Supabase 스키마는 별도 문서화 필요 시 추가)

## 보안 참고

- 이 문서에는 테이블 구조만 포함하며, **실제 데이터·비밀번호·접속 정보는 포함하지 않음.**
- DB 비밀번호는 `.env`에서 관리하며, 문서에 노출하지 않음.
