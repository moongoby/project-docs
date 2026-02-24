# 뉴톡 V1 — DB 스키마 요약 (autoda)

- 추출일: 2026-02-24 KST
- DB명: autoda
- 총 테이블 수: 226
- 읽기 전용. 스키마 참조 목적.

---

## 전체 테이블 목록

| # | 테이블명 |
|---|----------|
| 1 | NPLUS |
| 2 | aauth_groups |
| 3 | aauth_perm_to_group |
| 4 | aauth_perm_to_user |
| 5 | aauth_perms |
| 6 | aauth_pms |
| 7 | aauth_system_variables |
| 8 | aauth_user_to_group |
| 9 | aauth_user_variables |
| 10 | aauth_users |
| 11 | admin |
| 12 | aligo_template |
| 13 | arrival |
| 14 | arrival_block |
| 15 | arrival_block_new |
| 16 | auth_phone_number |
| 17 | banner |
| 18 | banner_modify_logs |
| 19 | board |
| 20 | board_ad |
| 21 | board_ci |
| 22 | board_ci_make |
| 23 | board_etc_qna |
| 24 | board_file |
| 25 | board_free |
| 26 | board_html5 |
| 27 | board_job |
| 28 | board_lecture |
| 29 | board_list |
| 30 | board_news |
| 31 | board_notice |
| 32 | board_qna |
| 33 | board_source |
| 34 | board_su |
| 35 | board_tip |
| 36 | building_info |
| 37 | building_sector_info |
| 38 | cafe24_logs |
| 39 | cafe24_settigs |
| 40 | cafe24_status |
| 41 | cafe24_token |
| 42 | ci_sessions |
| 43 | cjapi_token |
| 44 | click |
| 45 | codyImg_msg |
| 46 | cody_msg |
| 47 | cody_product_msg |
| 48 | company_groups |
| 49 | contents_msg |
| 50 | coupon_generate |
| 51 | coupon_setting |
| 52 | coupon_used |
| 53 | cron_reserve |
| 54 | cron_reserve_goods |
| 55 | cron_status |
| 56 | custom_push_msg |
| 57 | custom_push_msg_logs |
| 58 | customer |
| 59 | delivery_info |
| 60 | delivery_kind_logs |
| 61 | delivery_package_logs |
| 62 | delivery_package_price |
| 63 | deposit_refund |
| 64 | device_info |
| 65 | device_info_new |
| 66 | excel_data_result_log |
| 67 | faq_category |
| 68 | faq_category_modify_logs |
| 69 | faq_qa |
| 70 | faq_qa_modify_logs |
| 71 | files |
| 72 | goods |
| 73 | goods_20230830 |
| 74 | goods_20260106 |
| 75 | goods_action_logs |
| 76 | goods_banner |
| 77 | goods_best |
| 78 | goods_biz_logs |
| 79 | goods_cafe24 |
| 80 | goods_cate |
| 81 | goods_code |
| 82 | goods_code_image_compress_log |
| 83 | goods_color_list |
| 84 | goods_cron |
| 85 | goods_detail |
| 86 | goods_detail_backup_20260212_STEP6 |
| 87 | goods_detail_backup_20260212_STEP6_v3_0h_canary |
| 88 | goods_detail_backup_20260213_v32c |
| 89 | goods_detail_backup_20260213_v33b_desc |
| 90 | goods_detail_backup_test10_v32e5 |
| 91 | goods_detail_cron |
| 92 | goods_down |
| 93 | goods_down_status |
| 94 | goods_excel |
| 95 | goods_excel_new |
| 96 | goods_fit_list |
| 97 | goods_image |
| 98 | goods_image_compress_log |
| 99 | goods_image_cron |
| 100 | goods_image_down_price |
| 101 | goods_image_save_log |
| 102 | goods_master |
| 103 | goods_model_info |
| 104 | goods_model_modify_logs |
| 105 | goods_ocean |
| 106 | goods_only_logs |
| 107 | goods_option_code |
| 108 | goods_option_etc |
| 109 | goods_option_modify_logs |
| 110 | goods_sample |
| 111 | goods_size_info |
| 112 | goods_size_modify_logs |
| 113 | goods_watermark_config |
| 114 | goods_watermark_group |
| 115 | goods_watermark_icon |
| 116 | goods_watermark_icon_group |
| 117 | goods_watermark_img_code |
| 118 | goods_watermark_make |
| 119 | goods_watermark_setting |
| 120 | goods_watermark_setting_extend |
| 121 | goods_wholesale_contract |
| 122 | goods_wish |
| 123 | groups_name |
| 124 | kakao_template_list_for_message |
| 125 | login_attempts |
| 126 | mall_popup |
| 127 | market_goods_cate |
| 128 | market_goods_gosi |
| 129 | message |
| 130 | newtalk_template_msg |
| 131 | notice |
| 132 | notice_category |
| 133 | notice_category_modify_logs |
| 134 | notice_modify_logs |
| 135 | nt_name_mapping_cp |
| 136 | nt_name_mapping_cp_v2 |
| 137 | nt_name_mapping_dan |
| 138 | nt_name_mapping_ja |
| 139 | nt_name_mapping_ja_v2 |
| 140 | nt_name_pool |
| 141 | order_barcode |
| 142 | order_barcode_upload |
| 143 | order_block |
| 144 | order_block_alimTalk_logs |
| 145 | order_block_detail |
| 146 | order_block_modify_logs |
| 147 | order_block_new |
| 148 | order_norelease_modify_logs |
| 149 | order_product |
| 150 | order_product_box |
| 151 | order_product_status |
| 152 | order_request |
| 153 | order_search_logs |
| 154 | order_store_check_logs |
| 155 | ordered_items |
| 156 | orders |
| 157 | orders_old |
| 158 | pickup_delivered_batch |
| 159 | pickup_delivery_kind |
| 160 | pickup_delivery_kind_set |
| 161 | pickup_delivery_package |
| 162 | pickup_epost_invoice |
| 163 | pickup_hanjin_invoice |
| 164 | pickup_man_auth |
| 165 | pickup_man_auth_logs |
| 166 | pickup_request_chg |
| 167 | pigup_delivery_setting |
| 168 | pigup_order |
| 169 | pigup_request |
| 170 | pigup_request_old |
| 171 | pigup_setting |
| 172 | popup |
| 173 | push_reservation |
| 174 | sabangnet_id_info |
| 175 | search_words |
| 176 | shipping_address |
| 177 | site_log |
| 178 | sns_send_template_msg |
| 179 | sns_template_logs |
| 180 | store_ftp_config |
| 181 | tags |
| 182 | temp_user_profiles |
| 183 | use_end_day_history |
| 184 | user_apikey |
| 185 | user_autologin |
| 186 | user_client |
| 187 | user_company_match |
| 188 | user_delivery_partner |
| 189 | user_deposit |
| 190 | user_deposit_pg |
| 191 | user_down_service |
| 192 | user_employee |
| 193 | user_freelancer |
| 194 | user_id_update_logs |
| 195 | user_login_log |
| 196 | user_manager |
| 197 | user_manual_log |
| 198 | user_market |
| 199 | user_market_info |
| 200 | user_model |
| 201 | user_msg |
| 202 | user_msg_aligo |
| 203 | user_partner |
| 204 | user_partner_match |
| 205 | user_pay |
| 206 | user_place |
| 207 | user_popup_list |
| 208 | user_profiles |
| 209 | user_profiles_2109012314 |
| 210 | user_qna_group |
| 211 | user_qna_msg |
| 212 | user_sns |
| 213 | user_store_bookmark |
| 214 | user_template_msg |
| 215 | user_unregister_reason |
| 216 | user_wholeSale_log |
| 217 | user_wholesale_charge |
| 218 | user_wholesale_contract |
| 219 | user_wholesale_contract_history |
| 220 | users |
| 221 | users_2024062705 |
| 222 | users_2109012314 |
| 223 | v1_status |
| 224 | wholesale_billing_adjustment |
| 225 | wholesale_billing_draft |
| 226 | wholesale_billing_log |

## 핵심 테이블 구조

### aauth_perm_to_user
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
perm_id	int(11)	YES	MUL	NULL	
user_id	int(11)	YES		NULL	
```
행 수: 0

### aauth_user_to_group
```sql
Field	Type	Null	Key	Default	Extra
user_id	int(11)	NO	PRI	0	
group_id	int(11)	NO	PRI	0	
```
행 수: 2

### aauth_user_variables
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
user_id	int(11)	NO	MUL	NULL	
key	text	NO		NULL	
value	text	YES		NULL	
```
행 수: 0

### aauth_users
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
email	text	NO		NULL	
pass	text	NO		NULL	
name	text	YES		NULL	
banned	int(11)	YES		0	
last_login	datetime	YES		NULL	
last_activity	datetime	YES		NULL	
last_login_attempt	datetime	YES		NULL	
forgot_exp	text	YES		NULL	
remember_time	datetime	YES		NULL	
remember_exp	text	YES		NULL	
verification_code	text	YES		NULL	
ip_address	text	YES		NULL	
login_attempts	int(11)	YES		0	
```
행 수: 1

### cody_product_msg
```sql
Field	Type	Null	Key	Default	Extra
id	int(11) unsigned	NO	PRI	NULL	auto_increment
codyCode	varchar(255)	YES		NULL	
codyProdCode	varchar(255)	YES	MUL	NULL	
codyProdName	varchar(255)	YES		NULL	
codyProdColor	text	YES		NULL	
codyProdSize	text	YES		NULL	
codyProdNAS	text	YES		NULL	
codyProdMemo	varchar(255)	YES		NULL	
created	datetime	YES		NULL	
useCody	int(11)	YES		NULL	
shooting_id	int(11)	YES	MUL	NULL	
BizProgress	varchar(255)	YES		E1	
WebWorker	varchar(255)	YES		NULL	
TotalPriceWebworker	varchar(255)	YES		NULL	
WebWorkerDate	date	YES		NULL	
WebWorkerDoneDate	date	YES		NULL	
WebWorkerMemo	varchar(50)	YES		NULL	
WebWorkerNAS	varchar(4000)	YES		NULL	
Surcharge	varchar(255)	YES		NULL	
SurchargeContent	varchar(255)	YES		NULL	
PaymentStatus	tinyint(2)	YES		1	
GoodsEtc6	varchar(50)	YES		NULL	
PaymentDate	date	YES		NULL	
PaymentDoneDate	date	YES		NULL	
```
행 수: 8097

### company_groups
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
userid	int(11)	NO	MUL	NULL	
groupid	int(11)	NO	MUL	NULL	
companyid	int(11)	NO	MUL	NULL	
```
행 수: 23802

### coupon_generate
```sql
Field	Type	Null	Key	Default	Extra
cpg_no	int(11)	NO	PRI	NULL	auto_increment
cps_no	int(11)	NO		NULL	
cpg_user_id	int(11)	NO		NULL	
cpg_code	varchar(20)	YES	MUL	NULL	
cpg_regdate	datetime	YES		current_timestamp()	
```
행 수: 0

### coupon_setting
```sql
Field	Type	Null	Key	Default	Extra
cps_no	int(11)	NO	PRI	NULL	auto_increment
cps_user_id	int(11)	NO	MUL	NULL	
cps_title	varchar(100)	NO		NULL	
cps_content	varchar(255)	NO		NULL	
cps_group	char(1)	NO		NULL	
cps_type	char(1)	NO		NULL	
cps_method	char(1)	YES		NULL	
cps_limit	int(11)	YES		0	
cps_dc_type	char(1)	YES		NULL	
cps_dc_persent	int(11)	YES		NULL	
cps_dc_price	int(11)	NO		NULL	
cps_min_price	int(11)	YES		0	
cps_gen_opt	char(1)	YES		1	
cps_gen_sdate	varchar(12)	YES		NULL	
cps_gen_edate	varchar(12)	YES		NULL	
cps_use_opt	char(1)	YES		1	
cps_use_sdate	varchar(12)	YES		NULL	
cps_use_edate	varchar(12)	YES		NULL	
cps_use_day	smallint(6)	YES		NULL	
cps_status	tinyint(4)	YES		0	
cps_regdate	datetime	YES		current_timestamp()	
```
행 수: 0

### coupon_used
```sql
Field	Type	Null	Key	Default	Extra
cpu_no	int(11)	NO	PRI	NULL	auto_increment
cpg_no	int(11)	YES		NULL	
cpu_type	char(1)	YES		0	
request_id	int(11)	NO		NULL	
deposit_id	int(11)	NO		NULL	
cpu_org_price	int(11)	NO		NULL	
cpu_dc_price	int(11)	NO		NULL	
cpu_pay_price	int(11)	NO		NULL	
cpu_regdate	datetime	YES		current_timestamp()	
```
행 수: 0

### cron_reserve_goods
```sql
Field	Type	Null	Key	Default	Extra
cr_id	int(11)	NO	MUL	NULL	
goods_no	int(11) unsigned	NO		NULL	
GoodsNo	varchar(20)	NO		0	
```
행 수: 11

### delivery_info
```sql
Field	Type	Null	Key	Default	Extra
id	int(10) unsigned	NO	PRI	NULL	auto_increment
delivery_name	varchar(500)	NO		NULL	
delivery_code	varchar(255)	NO		NULL	
delivery_contact	varchar(255)	NO		NULL	
delivery_type	varchar(255)	NO		NULL	
size	varchar(255)	NO		NULL	
price	varchar(255)	NO		NULL	
etc	varchar(255)	NO		NULL	
use_yn	varchar(1)	NO		NULL	
```
행 수: 3

### delivery_kind_logs
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
delivery_id	int(11)	NO	MUL	0	
user_id	int(11)	NO	MUL	NULL	
column_name	varchar(30)	NO		NULL	
old_data	varchar(30)	YES		NULL	
new_data	varchar(30)	YES		NULL	
created	datetime	NO		0000-00-00 00:00:00	
```
행 수: 0

### delivery_package_logs
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
pack_id	int(11)	NO	MUL	0	
user_id	int(11)	NO	MUL	0	
column_name	varchar(30)	NO		NULL	
old_data	varchar(100)	YES		NULL	
new_data	varchar(100)	YES		NULL	
created	datetime	NO		0000-00-00 00:00:00	
```
행 수: 0

### delivery_package_price
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
pack_id	int(11)	NO	MUL	0	
user_id	int(11)	NO	MUL	0	
bi_id	int(11)	NO	MUL	0	
price	int(11) unsigned	NO		0	
use_yn	char(1)	NO		Y	
created	datetime	NO		0000-00-00 00:00:00	
```
행 수: 120

### faq_category
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
user_id	int(11)	NO	MUL	0	
category_name	varchar(30)	NO		NULL	
use_yn	char(1)	NO		Y	
created	datetime	YES		0000-00-00 00:00:00	
description	varchar(100)	YES		NULL	
ordered	int(11)	YES		NULL	
temp_desc	varchar(100)	YES		NULL	
```
행 수: 5

### faq_category_modify_logs
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
user_id	int(11)	NO	MUL	0	
category_id	int(11)	NO	MUL	0	
modify_name	varchar(20)	YES		NULL	
old_data	varchar(50)	YES		NULL	
modify_data	varchar(50)	YES		NULL	
created	datetime	YES		0000-00-00 00:00:00	
```
행 수: 521

### goods
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
user_id	int(11)	NO	MUL	NULL	
GdsMstId	int(11)	NO	MUL	0	
market	char(1)	NO	MUL	NULL	
Category1	varchar(50)	NO	MUL	NULL	
Category2	varchar(50)	NO	MUL	NULL	
Category3	varchar(50)	NO	MUL	NULL	
Category4	varchar(50)	YES		NULL	
GoodsName	varchar(50)	YES		NULL	
DanharooGoodsName	varchar(50)	YES		NULL	
GoodsCode_1	varchar(5)	YES		NULL	
GoodsCode_2	int(10)	YES		NULL	
GoodsCode_3	char(1)	YES		NULL	
GoodsCode_4	char(1)	YES		NULL	
GoodsCode_5	char(1)	YES		NULL	
GoodsCode_6	char(2)	YES		NULL	
GoodsCode	varchar(20)	NO	MUL	NULL	
CatalogName	varchar(50)	YES		NULL	
BrandName	varchar(50)	NO	MUL	NULL	
MakerName	varchar(50)	YES		NULL	
SellingPeriod	char(2)	YES		15	
SellingPeriodStart	varchar(50)	YES		0000-00-00	
SellingPeriodEnd	varchar(50)	YES		0000-00-00	
GoodsPrice	int(10) unsigned	YES		NULL	
GoodsCount	mediumint(5) unsigned	YES		NULL	
GoodsOptionsUseSetting	char(1)	YES		N	
GoodsImage	varchar(150)	YES		NULL	
CommonDeliveryWayOPTSEL	char(1)	YES		NULL	
DeliveryCOMP	char(5)	YES		NULL	
ShipmentPlaceNo	varchar(50)	YES		0	
DeliveryFeeType	char(1)	YES		NULL	
NoticeItemGroupNo	varchar(2)	YES		NULL	
GoodsNo	varchar(20)	YES		0	
OptionColor	varchar(300)	YES		NULL	
OptionSize	varchar(255)	YES		NULL	
OptionColorChina	varchar(255)	YES		NULL	
OptionSizeChina	varchar(255)	YES		NULL	
SocialGoodsOption	varchar(255)	YES		NULL	
OptionEtc	varchar(255)	YES		NULL	
OpenWho	char(1)	YES		1	
AfterDays	varchar(5)	YES		NULL	
MadeIn	char(1)	YES		0	
StyleW	varchar(50)	YES		NULL	
SendCount	smallint(4) unsigned	YES		0	
SendCheck	char(1)	NO	MUL	N	
GoodsEtc4	varchar(100)	YES		NULL	
GoodsEtc5	varchar(50)	YES		NULL	
GoodsEtc6	varchar(50)	NO	MUL	NULL	
GoodsEtc7	varchar(100)	YES		NULL	
GoodsEtc8	varchar(100)	YES		NULL	
GoodsEtc9	int(10) unsigned	YES		NULL	
GoodsEtc10	int(10) unsigned	YES		NULL	
GoodsEtc13	varchar(100)	YES		NULL	
GoodsEtc14_old	varchar(100)	YES		NULL	
GoodsEtc15_old	varchar(255)	YES		NULL	
GoodsEtc16	varchar(100)	YES		NULL	
GoodsEtc17	varchar(100)	YES		NULL	
GoodsEtc18	varchar(100)	YES		NULL	
GoodsEtc20	varchar(20)	YES		NULL	
GoodsEtc21	varchar(20)	YES		NULL	
GoodsEtc24	varchar(255)	YES		NULL	
GoodsEtc32	int(10) unsigned	YES		NULL	
GoodsEtc33	int(10) unsigned	YES		NULL	
GoodsEtc34	int(10) unsigned	YES		NULL	
GoodsEtc35	int(10) unsigned	YES		NULL	
GoodsEtc36	varchar(100)	YES		NULL	
GoodsEtc37	varchar(100)	YES		NULL	
GoodsEtc38	varchar(100)	YES		NULL	
GoodsEtc39	varchar(255)	YES		NULL	
GoodsEtc40	varchar(200)	YES		NULL	
GoodsEtc41	int(11) unsigned	YES		NULL	
GoodsEtc42	int(11) unsigned	YES		0	
GoodsEtc48	char(1)	YES		NULL	
GoodsEtc51	char(1)	YES		NULL	
GoodsEtc52	char(1)	NO	MUL	NULL	
GoodsEtc53	char(1)	YES		NULL	
GoodsEtc54	char(1)	YES		NULL	
GoodsEtc55	int(10) unsigned	YES		NULL	
GoodsEtc56	char(1)	YES		NULL	
GoodsEtc57	char(3)	YES		NULL	
GoodsOnly	char(1)	NO	MUL	N	
GoodsOnlyDay	date	NO	MUL	0000-00-00	
GoodsDetailSave	char(1)	YES		N	
GoodsDetailSaveDay	date	YES		0000-00-00	
GoodsEtc6Sort	int(10) unsigned	NO	MUL	0	
DeSkin	char(1)	YES		N	
MoSkin	char(1)	YES		N	
BizProgress	char(2)	NO	MUL	NULL	
BizProgressUpdate	datetime	NO	MUL	NULL	
InAdm	char(1)	YES		N	
activated	char(1)	NO	MUL	N	
activated_day	date	NO	MUL	0000-00-00	
mall_activated	char(1)	NO	MUL	N	
re_created	datetime	NO	MUL	NULL	
created	datetime	YES	MUL	0000-00-00 00:00:00	
modified	timestamp	YES		current_timestamp()	on update current_timestamp()
ddg_send_yn	varchar(10)	YES		N	
ddg_lastsend	datetime	YES		0000-00-00 00:00:00	
classify	varchar(255)	YES		NULL	
wholessaler	varchar(255)	YES		NULL	
wholessalerPrice	decimal(10,2)	YES		NULL	
OptionSizeDetail	varchar(255)	YES		NULL	
FabricFeel	text	YES		NULL	
AgeTarget	varchar(255)	YES		NULL	
FilmingRequestColor1	varchar(11)	YES		NULL	
FilmingRequestColor2	varchar(11)	YES		NULL	
FilmingRequestColor3	varchar(11)	YES		NULL	
FilmingRequestMemo	text	YES		NULL	
ShootingConceptSelect	varchar(50)	YES		NULL	
optionSizeDetail_value	text	YES		NULL	
optionSizeDetail_title	text	YES		NULL	
optionSizeDetail_entitle	text	YES		NULL	
AverageRating	varchar(55)	YES		NULL	
RatingToo	varchar(55)	YES		NULL	
StockingDate	date	YES	MUL	0000-00-00	
ModelShootingDate	date	YES		0000-00-00	
SampleReturnDate	date	YES		0000-00-00	
SampleStage	varchar(55)	YES	MUL	NULL	
WebWorker	varchar(255)	YES		NULL	
WebWorkerDate	date	YES		NULL	
WebWorkerDoneDate	date	YES		NULL	
WebWorkerNAS	varchar(255)	YES		NULL	
WebWorkerMemo	varchar(50)	YES		NULL	
NAS	varchar(255)	YES		NULL	
Photographer	varchar(255)	YES		NULL	
ProductShootingDate	date	YES		0000-00-00	
RatingTargetAge	varchar(255)	YES		NULL	
CodyCode	varchar(255)	YES		NULL	
useCody	int(11)	YES		1	
SetExtraAmount	varchar(255)	YES		NULL	
Surcharge	varchar(55)	YES		NULL	
SurchargeContent	varchar(255)	YES		NULL	
sabangnetDate	date	YES		NULL	
PaymentStatus	tinyint(1)	YES		0	
ExtraAmountSet	decimal(10,2)	YES		NULL	
TotalPriceWebworker	varchar(255)	YES		NULL	
WholeSale_code	varchar(55)	YES		NULL	
user_id_sale	int(11)	YES		NULL	
model_content	text	YES		NULL	
color_content	text	YES		NULL	
model_id	int(11)	YES		NULL	
```
행 수: 77132

### goods_20230830
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO		0	
user_id	int(11)	NO		NULL	
GdsMstId	int(11)	NO		0	
market	char(1)	NO		NULL	
Category1	varchar(50)	NO		NULL	
Category2	varchar(50)	NO		NULL	
Category3	varchar(50)	NO		NULL	
Category4	varchar(50)	NO		NULL	
GoodsName	varchar(50)	NO		NULL	
DanharooGoodsName	varchar(50)	NO		NULL	
GoodsCode_1	varchar(5)	NO		NULL	
GoodsCode_2	int(10)	NO		NULL	
GoodsCode_3	char(1)	NO		NULL	
GoodsCode_4	char(1)	NO		NULL	
GoodsCode_5	char(1)	NO		NULL	
GoodsCode_6	char(2)	YES		NULL	
GoodsCode	varchar(20)	NO		NULL	
CatalogName	varchar(50)	NO		NULL	
BrandName	varchar(50)	NO		NULL	
MakerName	varchar(50)	NO		NULL	
SellingPeriod	char(2)	NO		15	
SellingPeriodStart	date	NO		0000-00-00	
SellingPeriodEnd	date	NO		0000-00-00	
GoodsPrice	int(10) unsigned	NO		NULL	
GoodsCount	mediumint(5) unsigned	NO		NULL	
GoodsOptionsUseSetting	char(1)	NO		N	
GoodsImage	varchar(150)	NO		NULL	
CommonDeliveryWayOPTSEL	char(1)	NO		NULL	
DeliveryCOMP	char(5)	NO		NULL	
ShipmentPlaceNo	int(10)	NO		NULL	
DeliveryFeeType	char(1)	NO		NULL	
NoticeItemGroupNo	varchar(2)	NO		NULL	
GoodsNo	varchar(20)	NO		0	
OptionColor	varchar(300)	NO		NULL	
OptionSize	varchar(255)	NO		NULL	
OptionColorChina	varchar(255)	NO		NULL	
OptionSizeChina	varchar(255)	NO		NULL	
SocialGoodsOption	varchar(255)	NO		NULL	
OptionEtc	varchar(255)	NO		NULL	
OpenWho	char(1)	NO		1	
AfterDays	varchar(5)	NO		NULL	
MadeIn	char(1)	NO		0	
StyleW	varchar(2)	NO		NULL	
SendCount	smallint(4) unsigned	NO		0	
SendCheck	char(1)	NO		N	
GoodsEtc4	varchar(100)	NO		NULL	
GoodsEtc5	varchar(50)	NO		NULL	
GoodsEtc6	varchar(50)	NO		NULL	
GoodsEtc7	varchar(100)	NO		NULL	
GoodsEtc8	varchar(100)	NO		NULL	
GoodsEtc9	int(10) unsigned	NO		NULL	
GoodsEtc10	int(10) unsigned	NO		NULL	
GoodsEtc13	varchar(100)	NO		NULL	
GoodsEtc14_old	varchar(100)	NO		NULL	
GoodsEtc15_old	varchar(255)	NO		NULL	
GoodsEtc16	varchar(100)	NO		NULL	
GoodsEtc17	varchar(100)	NO		NULL	
GoodsEtc18	varchar(100)	NO		NULL	
GoodsEtc20	varchar(20)	NO		NULL	
GoodsEtc21	varchar(20)	NO		NULL	
GoodsEtc24	varchar(255)	NO		NULL	
GoodsEtc32	int(10) unsigned	NO		NULL	
GoodsEtc33	int(10) unsigned	NO		NULL	
GoodsEtc34	int(10) unsigned	NO		NULL	
GoodsEtc35	int(10) unsigned	NO		NULL	
GoodsEtc36	varchar(100)	NO		NULL	
GoodsEtc37	varchar(100)	NO		NULL	
GoodsEtc38	varchar(100)	NO		NULL	
GoodsEtc39	varchar(255)	NO		NULL	
GoodsEtc40	varchar(200)	NO		NULL	
GoodsEtc41	int(11) unsigned	NO		NULL	
GoodsEtc42	int(11) unsigned	NO		0	
GoodsEtc48	char(1)	NO		NULL	
GoodsEtc51	char(1)	NO		NULL	
GoodsEtc52	char(1)	NO		NULL	
GoodsEtc53	char(1)	NO		NULL	
GoodsEtc54	char(1)	NO		NULL	
GoodsEtc55	int(10) unsigned	NO		NULL	
GoodsEtc56	char(1)	NO		NULL	
GoodsEtc57	char(3)	NO		NULL	
GoodsOnly	char(1)	NO		N	
GoodsOnlyDay	date	NO		0000-00-00	
GoodsDetailSave	char(1)	NO		N	
GoodsDetailSaveDay	date	NO		0000-00-00	
GoodsEtc6Sort	int(10) unsigned	NO		0	
DeSkin	char(1)	NO		N	
MoSkin	char(1)	NO		N	
BizProgress	char(2)	NO		NULL	
BizProgressUpdate	datetime	NO		NULL	
InAdm	char(1)	NO		N	
activated	char(1)	NO		Y	
activated_day	date	NO		0000-00-00	
mall_activated	char(1)	NO		N	
re_created	datetime	NO		NULL	
created	datetime	NO		0000-00-00 00:00:00	
modified	timestamp	NO		current_timestamp()	on update current_timestamp()
ddg_send_yn	varchar(10)	NO		N	
ddg_lastsend	datetime	YES		0000-00-00 00:00:00	
```
행 수: 60897

### goods_20260106
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
user_id	int(11)	NO	MUL	NULL	
GdsMstId	int(11)	NO	MUL	0	
market	char(1)	NO	MUL	NULL	
Category1	varchar(50)	NO	MUL	NULL	
Category2	varchar(50)	NO	MUL	NULL	
Category3	varchar(50)	NO	MUL	NULL	
Category4	varchar(50)	YES		NULL	
GoodsName	varchar(50)	YES		NULL	
DanharooGoodsName	varchar(50)	YES		NULL	
GoodsCode_1	varchar(5)	YES		NULL	
GoodsCode_2	int(10)	YES		NULL	
GoodsCode_3	char(1)	YES		NULL	
GoodsCode_4	char(1)	YES		NULL	
GoodsCode_5	char(1)	YES		NULL	
GoodsCode_6	char(2)	YES		NULL	
GoodsCode	varchar(20)	NO	MUL	NULL	
CatalogName	varchar(50)	YES		NULL	
BrandName	varchar(50)	NO	MUL	NULL	
MakerName	varchar(50)	YES		NULL	
SellingPeriod	char(2)	YES		15	
SellingPeriodStart	varchar(50)	YES		0000-00-00	
SellingPeriodEnd	varchar(50)	YES		0000-00-00	
GoodsPrice	int(10) unsigned	YES		NULL	
GoodsCount	mediumint(5) unsigned	YES		NULL	
GoodsOptionsUseSetting	char(1)	YES		N	
GoodsImage	varchar(150)	YES		NULL	
CommonDeliveryWayOPTSEL	char(1)	YES		NULL	
DeliveryCOMP	char(5)	YES		NULL	
ShipmentPlaceNo	varchar(50)	YES		0	
DeliveryFeeType	char(1)	YES		NULL	
NoticeItemGroupNo	varchar(2)	YES		NULL	
GoodsNo	varchar(20)	YES		0	
OptionColor	varchar(300)	YES		NULL	
OptionSize	varchar(255)	YES		NULL	
OptionColorChina	varchar(255)	YES		NULL	
OptionSizeChina	varchar(255)	YES		NULL	
SocialGoodsOption	varchar(255)	YES		NULL	
OptionEtc	varchar(255)	YES		NULL	
OpenWho	char(1)	YES		1	
AfterDays	varchar(5)	YES		NULL	
MadeIn	char(1)	YES		0	
StyleW	varchar(50)	YES		NULL	
SendCount	smallint(4) unsigned	YES		0	
SendCheck	char(1)	NO	MUL	N	
GoodsEtc4	varchar(100)	YES		NULL	
GoodsEtc5	varchar(50)	YES		NULL	
GoodsEtc6	varchar(50)	NO	MUL	NULL	
GoodsEtc7	varchar(100)	YES		NULL	
GoodsEtc8	varchar(100)	YES		NULL	
GoodsEtc9	int(10) unsigned	YES		NULL	
GoodsEtc10	int(10) unsigned	YES		NULL	
GoodsEtc13	varchar(100)	YES		NULL	
GoodsEtc14_old	varchar(100)	YES		NULL	
GoodsEtc15_old	varchar(255)	YES		NULL	
GoodsEtc16	varchar(100)	YES		NULL	
GoodsEtc17	varchar(100)	YES		NULL	
GoodsEtc18	varchar(100)	YES		NULL	
GoodsEtc20	varchar(20)	YES		NULL	
GoodsEtc21	varchar(20)	YES		NULL	
GoodsEtc24	varchar(255)	YES		NULL	
GoodsEtc32	int(10) unsigned	YES		NULL	
GoodsEtc33	int(10) unsigned	YES		NULL	
GoodsEtc34	int(10) unsigned	YES		NULL	
GoodsEtc35	int(10) unsigned	YES		NULL	
GoodsEtc36	varchar(100)	YES		NULL	
GoodsEtc37	varchar(100)	YES		NULL	
GoodsEtc38	varchar(100)	YES		NULL	
GoodsEtc39	varchar(255)	YES		NULL	
GoodsEtc40	varchar(200)	YES		NULL	
GoodsEtc41	int(11) unsigned	YES		NULL	
GoodsEtc42	int(11) unsigned	YES		0	
GoodsEtc48	char(1)	YES		NULL	
GoodsEtc51	char(1)	YES		NULL	
GoodsEtc52	char(1)	NO	MUL	NULL	
GoodsEtc53	char(1)	YES		NULL	
GoodsEtc54	char(1)	YES		NULL	
GoodsEtc55	int(10) unsigned	YES		NULL	
GoodsEtc56	char(1)	YES		NULL	
GoodsEtc57	char(3)	YES		NULL	
GoodsOnly	char(1)	NO	MUL	N	
GoodsOnlyDay	date	NO	MUL	0000-00-00	
GoodsDetailSave	char(1)	YES		N	
GoodsDetailSaveDay	date	YES		0000-00-00	
GoodsEtc6Sort	int(10) unsigned	NO	MUL	0	
DeSkin	char(1)	YES		N	
MoSkin	char(1)	YES		N	
BizProgress	char(2)	NO	MUL	NULL	
BizProgressUpdate	datetime	NO	MUL	NULL	
InAdm	char(1)	YES		N	
activated	char(1)	NO	MUL	N	
activated_day	date	NO	MUL	0000-00-00	
mall_activated	char(1)	NO	MUL	N	
re_created	datetime	NO	MUL	NULL	
created	datetime	YES		0000-00-00 00:00:00	
modified	timestamp	YES		current_timestamp()	on update current_timestamp()
ddg_send_yn	varchar(10)	YES		N	
ddg_lastsend	datetime	YES		0000-00-00 00:00:00	
classify	varchar(255)	YES		NULL	
wholessaler	varchar(255)	YES		NULL	
wholessalerPrice	decimal(10,2)	YES		NULL	
OptionSizeDetail	varchar(255)	YES		NULL	
FabricFeel	text	YES		NULL	
AgeTarget	varchar(255)	YES		NULL	
FilmingRequestColor1	varchar(11)	YES		NULL	
FilmingRequestColor2	varchar(11)	YES		NULL	
FilmingRequestColor3	varchar(11)	YES		NULL	
FilmingRequestMemo	text	YES		NULL	
ShootingConceptSelect	varchar(50)	YES		NULL	
optionSizeDetail_value	text	YES		NULL	
optionSizeDetail_title	text	YES		NULL	
optionSizeDetail_entitle	text	YES		NULL	
AverageRating	varchar(55)	YES		NULL	
RatingToo	varchar(55)	YES		NULL	
StockingDate	date	YES	MUL	0000-00-00	
ModelShootingDate	date	YES		0000-00-00	
SampleReturnDate	date	YES		0000-00-00	
SampleStage	varchar(55)	YES		NULL	
WebWorker	varchar(255)	YES		NULL	
WebWorkerDate	date	YES		NULL	
WebWorkerDoneDate	date	YES		NULL	
WebWorkerNAS	varchar(255)	YES		NULL	
WebWorkerMemo	varchar(50)	YES		NULL	
NAS	varchar(255)	YES		NULL	
Photographer	varchar(255)	YES		NULL	
ProductShootingDate	date	YES		0000-00-00	
RatingTargetAge	varchar(255)	YES		NULL	
CodyCode	varchar(255)	YES		NULL	
useCody	int(11)	YES		1	
SetExtraAmount	varchar(255)	YES		NULL	
Surcharge	varchar(55)	YES		NULL	
SurchargeContent	varchar(255)	YES		NULL	
sabangnetDate	date	YES		NULL	
PaymentStatus	tinyint(1)	YES		0	
ExtraAmountSet	decimal(10,2)	YES		NULL	
TotalPriceWebworker	varchar(255)	YES		NULL	
WholeSale_code	varchar(55)	YES		NULL	
user_id_sale	int(11)	YES		NULL	
model_content	text	YES		NULL	
color_content	text	YES		NULL	
model_id	int(11)	YES		NULL	
```
행 수: 76603

### goods_action_logs
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
gb	char(1)	NO	MUL	X	
user_id	int(11)	NO	MUL	0	
goods_id	int(11)	NO	MUL	NULL	
user_ip	varchar(40)	NO		NULL	
regdate	timestamp	NO		current_timestamp()	on update current_timestamp()
```
행 수: 1043403

### goods_banner
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
user_id	int(11)	NO	MUL	NULL	
goods_id	int(11)	NO	MUL	NULL	
filename	varchar(50)	NO		NULL	
sort	tinyint(2) unsigned	NO		0	
set_ip	varchar(25)	NO		NULL	
created	datetime	NO		0000-00-00 00:00:00	
modified	timestamp	NO		current_timestamp()	on update current_timestamp()
```
행 수: 1386

### goods_best
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
user_id	int(11)	NO	MUL	NULL	
goods_id	int(11)	NO	MUL	NULL	
checking	char(1)	NO	MUL	NULL	
check_ip	varchar(25)	NO		NULL	
created	datetime	NO		0000-00-00 00:00:00	
modified	timestamp	NO		current_timestamp()	on update current_timestamp()
```
행 수: 15832

### goods_biz_logs
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
gb	char(2)	NO	MUL	NULL	
user_id	int(11)	NO	MUL	0	
goods_id	int(11)	NO	MUL	NULL	
user_ip	varchar(40)	NO		NULL	
regdate	timestamp	NO		current_timestamp()	on update current_timestamp()
```
행 수: 157071

### goods_cafe24
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
user_id	int(11)	NO	MUL	NULL	
goods_id	int(11)	NO	MUL	NULL	
mall_id	varchar(30)	NO	MUL	NULL	
product_no	int(11) unsigned	NO		0	
product_code	varchar(20)	NO		NULL	
product_name	varchar(50)	NO		NULL	
price	int(10) unsigned	NO		0	
small_image	varchar(200)	NO		NULL	
send_ip	varchar(25)	NO		NULL	
created	datetime	NO		0000-00-00 00:00:00	
modified	timestamp	NO		current_timestamp()	on update current_timestamp()
```
행 수: 334455

### goods_cate
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
market	char(1)	NO	MUL	NULL	
LargeCategory	varchar(50)	NO		NULL	
LargeCode	varchar(20)	NO		NULL	
MiddleCategory	varchar(50)	NO		NULL	
MiddleCode	varchar(20)	NO		NULL	
SmallCategory	varchar(50)	NO		NULL	
SmallCode	varchar(20)	NO		NULL	
DetailCategory	varchar(50)	NO		NULL	
CategoryCode	varchar(20)	NO		NULL	
hashtag	varchar(255)	YES		NULL	
activated	char(1)	NO	MUL	Y	
created	datetime	NO		0000-00-00 00:00:00	
modified	timestamp	NO		current_timestamp()	on update current_timestamp()
```
행 수: 33520

### goods_code
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
gcode	varchar(20)	NO	UNI	NULL	
activated	tinyint(1) unsigned	NO		1	
filecnt	smallint(3) unsigned	NO	MUL	0	
filecnt_update	datetime	NO		0000-00-00 00:00:00	
created	datetime	NO		0000-00-00 00:00:00	
modified	timestamp	NO		current_timestamp()	on update current_timestamp()
```
행 수: 78062

### goods_code_image_compress_log
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
goodscode	varchar(20)	NO		NULL	
filename	varchar(100)	NO	MUL	NULL	
dirname	varchar(100)	NO		NULL	
original_byte	varchar(20)	NO		NULL	
compress_byte	varchar(100)	YES		NULL	
filemtime	datetime	NO		NULL	
created	timestamp	NO		current_timestamp()	on update current_timestamp()
```
행 수: 485671

### goods_color_list
```sql
Field	Type	Null	Key	Default	Extra
gcl_no	int(11)	NO	PRI	NULL	auto_increment
gcl_user_id	int(11)	NO	MUL	NULL	
gcl_kr	varchar(10)	NO		NULL	
gcl_en	varchar(20)	NO		NULL	
gcl_regdate	datetime	YES		NULL	
```
행 수: 139

### goods_cron
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
user_id	int(11)	NO	MUL	NULL	
GdsMstId	int(11)	NO	MUL	0	
market	char(1)	NO	MUL	NULL	
Category1	varchar(50)	NO		NULL	
Category2	varchar(50)	NO		NULL	
Category3	varchar(50)	NO		NULL	
Category4	varchar(50)	NO		NULL	
GoodsName	varchar(50)	NO		NULL	
CatalogName	varchar(50)	NO		NULL	
BrandName	varchar(50)	NO		NULL	
MakerName	varchar(50)	NO		NULL	
SellingPeriod	char(2)	NO		15	
SellingPeriodStart	date	NO		0000-00-00	
SellingPeriodEnd	date	NO		0000-00-00	
GoodsPrice	int(10) unsigned	NO		NULL	
GoodsCount	mediumint(5) unsigned	NO		NULL	
GoodsOptionsUseSetting	char(1)	NO		N	
GoodsImage	varchar(150)	NO		NULL	
CommonDeliveryWayOPTSEL	char(1)	NO		NULL	
DeliveryCOMP	char(5)	NO		NULL	
ShipmentPlaceNo	int(10)	NO		NULL	
DeliveryFeeType	char(1)	NO		NULL	
NoticeItemGroupNo	varchar(2)	NO		NULL	
GoodsNo	varchar(20)	NO		0	
OptionColor	varchar(255)	NO		NULL	
OptionSize	varchar(255)	NO		NULL	
OptionEtc	varchar(255)	NO		NULL	
OpenWho	char(1)	NO		1	
AfterDays	varchar(5)	NO		NULL	
MadeIn	char(1)	NO		0	
StyleW	varchar(2)	NO		NULL	
DelGb	char(1)	NO		N	
activated	tinyint(1) unsigned	NO		0	
created	datetime	NO		0000-00-00 00:00:00	
modified	timestamp	NO		current_timestamp()	on update current_timestamp()
```
행 수: 21470

### goods_detail
```sql
Field	Type	Null	Key	Default	Extra
gd_id	int(11)	NO	PRI	NULL	auto_increment
goods_id	int(11)	NO	UNI	NULL	
GoodsOptVal	text	YES		NULL	
Description	text	YES		NULL	
NoticeItemCodes	text	YES		NULL	
DanharooDescription	text	YES		NULL	
GoodsInsertJson	text	YES		NULL	
MarketInsertJson	text	YES		NULL	
GoodsEtc14	text	YES		NULL	
GoodsEtc15	text	YES		NULL	
GoodsEtc22	text	YES		NULL	
GoodsEtc25	text	YES		NULL	
GoodsEtc26	text	YES		NULL	
GoodsEtc27	text	YES		NULL	
GoodsEtc28	text	YES		NULL	
GoodsEtc29	text	YES		NULL	
GoodsEtc30	text	YES		NULL	
GoodsEtc58	text	YES		NULL	
GoodsEtc59	text	YES		NULL	
GoodsEtc60	varchar(100)	YES		NULL	
GoodsEtc61	varchar(100)	YES		NULL	
GoodsEtc62	varchar(100)	YES		NULL	
GoodsEtc63	varchar(100)	YES		NULL	
GoodsEtc64	varchar(100)	YES		NULL	
GoodsEtc65	varchar(100)	YES		NULL	
GoodsEtc66	varchar(100)	YES		NULL	
GoodsEtc67	varchar(100)	YES		NULL	
GoodsEtc68	varchar(100)	YES		NULL	
GoodsEtc69	varchar(100)	YES		NULL	
GoodsEtc70	varchar(100)	YES		NULL	
GoodsEtc71	varchar(100)	YES		NULL	
GoodsEtc72	varchar(100)	YES		NULL	
GoodsEtc73	varchar(100)	YES		NULL	
GoodsEtc74	varchar(100)	YES		NULL	
GoodsMovieUrl	varchar(255)	YES		NULL	
GoodsSortImg1	text	YES		NULL	
GoodsSortImg2	text	YES		NULL	
GoodsSortImg3	text	YES		NULL	
GoodsSortImg4	text	YES		NULL	
GoodsEtcSerializes	text	YES		NULL	
CoordiGoodsCodes	varchar(100)	YES		NULL	
modified	timestamp	NO		current_timestamp()	on update current_timestamp()
```
행 수: 77138

### goods_detail_backup_20260212_STEP6
```sql
Field	Type	Null	Key	Default	Extra
gd_id	int(11)	NO		0	
goods_id	int(11)	NO		NULL	
GoodsOptVal	text	YES		NULL	
Description	text	YES		NULL	
NoticeItemCodes	text	YES		NULL	
DanharooDescription	text	YES		NULL	
GoodsInsertJson	text	YES		NULL	
MarketInsertJson	text	YES		NULL	
GoodsEtc14	text	YES		NULL	
GoodsEtc15	text	YES		NULL	
GoodsEtc22	text	YES		NULL	
GoodsEtc25	text	YES		NULL	
GoodsEtc26	text	YES		NULL	
GoodsEtc27	text	YES		NULL	
GoodsEtc28	text	YES		NULL	
GoodsEtc29	text	YES		NULL	
GoodsEtc30	text	YES		NULL	
GoodsEtc58	text	YES		NULL	
GoodsEtc59	text	YES		NULL	
GoodsEtc60	varchar(100)	YES		NULL	
GoodsEtc61	varchar(100)	YES		NULL	
GoodsEtc62	varchar(100)	YES		NULL	
GoodsEtc63	varchar(100)	YES		NULL	
GoodsEtc64	varchar(100)	YES		NULL	
GoodsEtc65	varchar(100)	YES		NULL	
GoodsEtc66	varchar(100)	YES		NULL	
GoodsEtc67	varchar(100)	YES		NULL	
GoodsEtc68	varchar(100)	YES		NULL	
GoodsEtc69	varchar(100)	YES		NULL	
GoodsEtc70	varchar(100)	YES		NULL	
GoodsEtc71	varchar(100)	YES		NULL	
GoodsEtc72	varchar(100)	YES		NULL	
GoodsEtc73	varchar(100)	YES		NULL	
GoodsEtc74	varchar(100)	YES		NULL	
GoodsMovieUrl	varchar(255)	YES		NULL	
GoodsSortImg1	text	YES		NULL	
GoodsSortImg2	text	YES		NULL	
GoodsSortImg3	text	YES		NULL	
GoodsSortImg4	text	YES		NULL	
GoodsEtcSerializes	text	YES		NULL	
CoordiGoodsCodes	varchar(100)	YES		NULL	
modified	timestamp	NO		current_timestamp()	on update current_timestamp()
```
행 수: 46055

### goods_detail_backup_20260212_STEP6_v3_0h_canary
```sql
Field	Type	Null	Key	Default	Extra
goods_id	int(11)	NO		NULL	
GoodsEtc60	varchar(100)	YES		NULL	
GoodsEtc61	varchar(100)	YES		NULL	
GoodsEtc62	varchar(100)	YES		NULL	
GoodsEtc63	varchar(100)	YES		NULL	
GoodsEtc64	varchar(100)	YES		NULL	
GoodsEtc65	varchar(100)	YES		NULL	
GoodsEtc66	varchar(100)	YES		NULL	
GoodsEtc67	varchar(100)	YES		NULL	
GoodsEtc68	varchar(100)	YES		NULL	
GoodsEtc69	varchar(100)	YES		NULL	
GoodsEtc70	varchar(100)	YES		NULL	
GoodsEtc71	varchar(100)	YES		NULL	
GoodsEtc72	varchar(100)	YES		NULL	
GoodsEtc73	varchar(100)	YES		NULL	
GoodsEtc74	varchar(100)	YES		NULL	
```
행 수: 5

### goods_detail_backup_20260213_v32c
```sql
Field	Type	Null	Key	Default	Extra
gd_id	int(11)	NO		0	
goods_id	int(11)	NO		NULL	
GoodsOptVal	text	YES		NULL	
Description	text	YES		NULL	
NoticeItemCodes	text	YES		NULL	
DanharooDescription	text	YES		NULL	
GoodsInsertJson	text	YES		NULL	
MarketInsertJson	text	YES		NULL	
GoodsEtc14	text	YES		NULL	
GoodsEtc15	text	YES		NULL	
GoodsEtc22	text	YES		NULL	
GoodsEtc25	text	YES		NULL	
GoodsEtc26	text	YES		NULL	
GoodsEtc27	text	YES		NULL	
GoodsEtc28	text	YES		NULL	
GoodsEtc29	text	YES		NULL	
GoodsEtc30	text	YES		NULL	
GoodsEtc58	text	YES		NULL	
GoodsEtc59	text	YES		NULL	
GoodsEtc60	varchar(100)	YES		NULL	
GoodsEtc61	varchar(100)	YES		NULL	
GoodsEtc62	varchar(100)	YES		NULL	
GoodsEtc63	varchar(100)	YES		NULL	
GoodsEtc64	varchar(100)	YES		NULL	
GoodsEtc65	varchar(100)	YES		NULL	
GoodsEtc66	varchar(100)	YES		NULL	
GoodsEtc67	varchar(100)	YES		NULL	
GoodsEtc68	varchar(100)	YES		NULL	
GoodsEtc69	varchar(100)	YES		NULL	
GoodsEtc70	varchar(100)	YES		NULL	
GoodsEtc71	varchar(100)	YES		NULL	
GoodsEtc72	varchar(100)	YES		NULL	
GoodsEtc73	varchar(100)	YES		NULL	
GoodsEtc74	varchar(100)	YES		NULL	
GoodsMovieUrl	varchar(255)	YES		NULL	
GoodsSortImg1	text	YES		NULL	
GoodsSortImg2	text	YES		NULL	
GoodsSortImg3	text	YES		NULL	
GoodsSortImg4	text	YES		NULL	
GoodsEtcSerializes	text	YES		NULL	
CoordiGoodsCodes	varchar(100)	YES		NULL	
modified	timestamp	NO		current_timestamp()	on update current_timestamp()
```
행 수: 77089

### goods_detail_backup_20260213_v33b_desc
```sql
Field	Type	Null	Key	Default	Extra
goods_id	int(11)	NO		NULL	
DanharooDescription	text	YES		NULL	
```
행 수: 55015

### goods_detail_backup_test10_v32e5
```sql
Field	Type	Null	Key	Default	Extra
gd_id	int(11)	NO		0	
goods_id	int(11)	NO		NULL	
GoodsOptVal	text	YES		NULL	
Description	text	YES		NULL	
NoticeItemCodes	text	YES		NULL	
DanharooDescription	text	YES		NULL	
GoodsInsertJson	text	YES		NULL	
MarketInsertJson	text	YES		NULL	
GoodsEtc14	text	YES		NULL	
GoodsEtc15	text	YES		NULL	
GoodsEtc22	text	YES		NULL	
GoodsEtc25	text	YES		NULL	
GoodsEtc26	text	YES		NULL	
GoodsEtc27	text	YES		NULL	
GoodsEtc28	text	YES		NULL	
GoodsEtc29	text	YES		NULL	
GoodsEtc30	text	YES		NULL	
GoodsEtc58	text	YES		NULL	
GoodsEtc59	text	YES		NULL	
GoodsEtc60	varchar(100)	YES		NULL	
GoodsEtc61	varchar(100)	YES		NULL	
GoodsEtc62	varchar(100)	YES		NULL	
GoodsEtc63	varchar(100)	YES		NULL	
GoodsEtc64	varchar(100)	YES		NULL	
GoodsEtc65	varchar(100)	YES		NULL	
GoodsEtc66	varchar(100)	YES		NULL	
GoodsEtc67	varchar(100)	YES		NULL	
GoodsEtc68	varchar(100)	YES		NULL	
GoodsEtc69	varchar(100)	YES		NULL	
GoodsEtc70	varchar(100)	YES		NULL	
GoodsEtc71	varchar(100)	YES		NULL	
GoodsEtc72	varchar(100)	YES		NULL	
GoodsEtc73	varchar(100)	YES		NULL	
GoodsEtc74	varchar(100)	YES		NULL	
GoodsMovieUrl	varchar(255)	YES		NULL	
GoodsSortImg1	text	YES		NULL	
GoodsSortImg2	text	YES		NULL	
GoodsSortImg3	text	YES		NULL	
GoodsSortImg4	text	YES		NULL	
GoodsEtcSerializes	text	YES		NULL	
CoordiGoodsCodes	varchar(100)	YES		NULL	
modified	timestamp	NO		current_timestamp()	on update current_timestamp()
```
행 수: 10

### goods_detail_cron
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
goods_id	int(11)	NO	UNI	NULL	
GoodsOptVal	text	NO		NULL	
Description	text	NO		NULL	
NoticeItemCodes	text	NO		NULL	
GoodsInsertJson	text	NO		NULL	
MarketInsertJson	text	NO		NULL	
modified	timestamp	NO		current_timestamp()	on update current_timestamp()
```
행 수: 21470

### goods_down
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
user_id	int(11)	NO	MUL	NULL	
goods_id	int(11)	NO	MUL	NULL	
downing	char(1)	NO	MUL	NULL	
down_ip	varchar(25)	NO		NULL	
soldout_del	char(1)	NO		N	
soldout_date	datetime	NO		0000-00-00 00:00:00	
created	datetime	NO		0000-00-00 00:00:00	
down_modified	timestamp	NO		current_timestamp()	on update current_timestamp()
```
행 수: 333828

### goods_down_status
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
gb	char(1)	NO	MUL	P	
user_id	int(11)	NO	MUL	0	
goods_id	int(11)	NO	MUL	NULL	
goods_code	varchar(20)	NO	MUL	NULL	
user_ip	varchar(40)	NO		NULL	
regdate	timestamp	NO		current_timestamp()	on update current_timestamp()
```
행 수: 1992183

### goods_excel
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
GoodsCode	varchar(20)	NO	MUL	NULL	
GoodsName	varchar(50)	NO		NULL	
GoodsOption	varchar(200)	NO		NULL	
GoodsCount	varchar(5)	NO	MUL	0	
GoodsCountX	int(10) unsigned	NO		0	
GoodsCountY	int(10) unsigned	NO		0	
GoodsPrice1	int(10) unsigned	NO		NULL	
GoodsPrice2	int(10) unsigned	NO		NULL	
GoodsPrice3	int(10) unsigned	NO		NULL	
GoodsPrice4	int(10) unsigned	NO		NULL	
GoodsPrice5	int(10) unsigned	NO		NULL	
GoodsPrice1Title	varchar(50)	NO		NULL	
GoodsPrice2Title	varchar(50)	NO		NULL	
GoodsPrice3Title	varchar(50)	NO		NULL	
GoodsPrice4Title	varchar(50)	NO		NULL	
GoodsPrice5Title	varchar(50)	NO		NULL	
ConfirmSetNo	int(10) unsigned	NO		0	
ConfirmWiNo	int(10) unsigned	NO		0	
created	datetime	NO		0000-00-00 00:00:00	
modified	timestamp	NO		current_timestamp()	on update current_timestamp()
```
행 수: 953

### goods_excel_new
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
user_id	int(11) unsigned	NO	MUL	0	
GoodsCode	varchar(20)	NO	MUL	NULL	
GoodsName	varchar(50)	NO		NULL	
GoodsOption	varchar(200)	NO		NULL	
GoodsCount	varchar(5)	NO	MUL	0	
GoodsCountX	int(10) unsigned	NO		0	
GoodsCountY	int(10) unsigned	NO		0	
GoodsPrice1	int(10) unsigned	NO		NULL	
GoodsPrice2	int(10) unsigned	NO		NULL	
GoodsPrice3	int(10) unsigned	NO		NULL	
GoodsPrice4	int(10) unsigned	NO		NULL	
GoodsPrice5	int(10) unsigned	NO		NULL	
GoodsPrice1Title	varchar(50)	NO		NULL	
GoodsPrice2Title	varchar(50)	NO		NULL	
GoodsPrice3Title	varchar(50)	NO		NULL	
GoodsPrice4Title	varchar(50)	NO		NULL	
GoodsPrice5Title	varchar(50)	NO		NULL	
ConfirmSetNo	int(10) unsigned	NO		0	
ConfirmWiNo	int(10) unsigned	NO		0	
created	datetime	NO		0000-00-00 00:00:00	
modified	timestamp	NO		current_timestamp()	on update current_timestamp()
```
행 수: 1618

### goods_fit_list
```sql
Field	Type	Null	Key	Default	Extra
gfl_no	int(11)	NO	PRI	NULL	auto_increment
gfl_user_id	int(11)	NO	MUL	NULL	
gfl_fit	varchar(80)	NO		NULL	
gfl_regdate	datetime	YES		NULL	
```
행 수: 22

### goods_image
```sql
Field	Type	Null	Key	Default	Extra
gi_id	int(11)	NO	PRI	NULL	auto_increment
goods_id	int(11)	NO	UNI	NULL	
img0	varchar(150)	YES		NULL	
img1	varchar(100)	YES		NULL	
img2	varchar(100)	YES		NULL	
img3	varchar(100)	YES		NULL	
img4	varchar(100)	YES		NULL	
img5	varchar(100)	YES		NULL	
img6	varchar(100)	YES		NULL	
img7	varchar(100)	YES		NULL	
img8	varchar(100)	YES		NULL	
img9	varchar(100)	YES		NULL	
img10	varchar(100)	YES		NULL	
img11	varchar(100)	YES		NULL	
img12	varchar(100)	YES		NULL	
img13	varchar(100)	YES		NULL	
img14	varchar(100)	YES		NULL	
img15	varchar(100)	YES		NULL	
img16	varchar(100)	YES		NULL	
img17	varchar(100)	YES		NULL	
img18	varchar(100)	YES		NULL	
img19	varchar(100)	YES		NULL	
img_etc0	varchar(100)	YES		NULL	
img_etc1	varchar(100)	YES		NULL	
img_etc2	varchar(100)	YES		NULL	
img_etc3	varchar(100)	YES		NULL	
img_etc4	varchar(100)	YES		NULL	
img_etc5	varchar(100)	YES		NULL	
img_etc6	varchar(100)	YES		NULL	
img_etc7	varchar(100)	YES		NULL	
img_etc8	varchar(100)	YES		NULL	
img_etc9	varchar(100)	YES		NULL	
modified	timestamp	NO		current_timestamp()	on update current_timestamp()
```
행 수: 76914

### goods_image_compress_log
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
filename	varchar(100)	NO	MUL	NULL	
dirname	varchar(100)	NO		NULL	
original_byte	varchar(20)	NO		NULL	
compress_byte	varchar(100)	NO		NULL	
filemtime	datetime	NO		NULL	
created	timestamp	NO		current_timestamp()	on update current_timestamp()
```
행 수: 28711

### goods_image_cron
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
goods_id	int(11)	NO	UNI	NULL	
img0	varchar(150)	NO		NULL	
img1	varchar(100)	NO		NULL	
img2	varchar(100)	NO		NULL	
img3	varchar(100)	NO		NULL	
img4	varchar(100)	NO		NULL	
img5	varchar(100)	NO		NULL	
img6	varchar(100)	NO		NULL	
img7	varchar(100)	NO		NULL	
img8	varchar(100)	NO		NULL	
img9	varchar(100)	NO		NULL	
img10	varchar(100)	NO		NULL	
img11	varchar(100)	NO		NULL	
img12	varchar(100)	NO		NULL	
img13	varchar(100)	NO		NULL	
img14	varchar(100)	NO		NULL	
modified	timestamp	NO		current_timestamp()	on update current_timestamp()
```
행 수: 21470

### goods_image_down_price
```sql
Field	Type	Null	Key	Default	Extra
svc_id	tinyint(4)	NO	PRI	NULL	
svc_name	varchar(50)	NO		NULL	
svc_down_cnt	smallint(6)	YES		0	
svc_price	int(11)	YES		0	
svc_dc_rate	smallint(6)	YES		0	
svc_pg_price	int(11)	YES		0	
```
행 수: 7

### goods_image_save_log
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
goodsno	int(10) unsigned	NO	MUL	0	
goodsuse	char(1)	NO	MUL	N	
filename	varchar(100)	NO	UNI	NULL	
dirname	varchar(100)	NO		NULL	
original_byte	int(10)	NO		0	
filemtime	datetime	NO		NULL	
goodsusedtime	datetime	NO		0000-00-00 00:00:00	
goodsdeletetime	datetime	NO		0000-00-00 00:00:00	
created	timestamp	NO		current_timestamp()	on update current_timestamp()
```
행 수: 481560

### goods_master
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
user_id	int(11)	NO	MUL	NULL	
Category1	varchar(50)	YES		NULL	
Category2	varchar(50)	YES		NULL	
Category3	varchar(50)	YES		NULL	
Category4	varchar(50)	YES		NULL	
GoodsName	varchar(50)	YES		NULL	
GoodsCode	varchar(20)	YES		NULL	
CatalogName	varchar(50)	YES		NULL	
BrandName	varchar(50)	YES		NULL	
MakerName	varchar(50)	YES		NULL	
SellingPeriod	char(2)	NO		15	
SellingPeriodStart	varchar(50)	YES			
SellingPeriodEnd	varchar(50)	YES			
GoodsPrice	int(10)	NO		0	
GoodsCount	mediumint(5)	NO		0	
GoodsOptionsUseSetting	char(1)	YES		N	
GoodsImage	varchar(150)	YES		NULL	
CommonDeliveryWayOPTSEL	char(1)	YES		NULL	
DeliveryCOMP	char(5)	YES		NULL	
ShipmentPlaceNo	varchar(10)	YES		0	
DeliveryFeeType	char(1)	YES		NULL	
NoticeItemGroupNo	varchar(2)	YES		NULL	
activated	tinyint(1) unsigned	YES		0	
created	datetime	YES		0000-00-00 00:00:00	
modified	timestamp	YES		current_timestamp()	on update current_timestamp()
```
행 수: 87656

### goods_model_info
```sql
Field	Type	Null	Key	Default	Extra
gmi_no	int(11)	NO	PRI	NULL	auto_increment
gmi_user_id	int(11)	NO	MUL	NULL	
gmi_name	varchar(40)	NO		NULL	
gmi_top	varchar(10)	YES		NULL	
gmi_bust	varchar(10)	YES		NULL	
gmi_pants	varchar(10)	YES		NULL	
gmi_height	varchar(10)	YES		NULL	
gmi_shoes	varchar(10)	YES		NULL	
gmi_use_yn	char(1)	NO		Y	
gmi_regdate	datetime	YES		NULL	
```
행 수: 33

### goods_model_modify_logs
```sql
Field	Type	Null	Key	Default	Extra
gmml_no	int(11)	NO	PRI	NULL	auto_increment
gmi_no	int(11)	NO	MUL	NULL	
gmml_user_id	int(11)	NO	MUL	NULL	
gmml_content	varchar(50)	NO		NULL	
gmml_old_data	varchar(80)	YES		NULL	
gmml_new_data	varchar(80)	YES		NULL	
gmml_regdate	datetime	YES		NULL	
```
행 수: 72

### goods_ocean
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
goods_id	int(11)	NO		NULL	
goods_code	varchar(250)	NO		NULL	
goods_fileName	varchar(500)	NO		NULL	
goods_msg	varchar(500)	NO		NULL	
reg_date	datetime	NO		current_timestamp()	
```
행 수: 1527288

### goods_only_logs
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
before	char(1)	NO		NULL	
after	char(1)	NO		NULL	
user_id	int(11)	NO	MUL	0	
goods_id	int(11)	NO	MUL	NULL	
user_ip	varchar(40)	NO		NULL	
regdate	timestamp	NO		current_timestamp()	on update current_timestamp()
```
행 수: 13408

### goods_option_code
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
goods_id	int(11) unsigned	NO	MUL	0	
code	char(4)	NO		0000	
size	varchar(50)	NO		NULL	
color	varchar(50)	NO		NULL	
created	datetime	NO		0000-00-00 00:00:00	
modified	timestamp	NO		current_timestamp()	on update current_timestamp()
```
행 수: 129226

### goods_option_etc
```sql
Field	Type	Null	Key	Default	Extra
goe_no	int(11)	NO	PRI	NULL	auto_increment
goe_user_id	int(11)	NO	MUL	NULL	
goe_name	varchar(20)	NO	MUL	NULL	
goe_key	varchar(10)	NO		NULL	
goe_value	varchar(50)	NO		NULL	
use_yn	char(1)	NO		Y	
goe_regdate	datetime	YES		NULL	
```
행 수: 55

### goods_option_modify_logs
```sql
Field	Type	Null	Key	Default	Extra
goml_no	int(11)	NO	PRI	NULL	auto_increment
goe_no	int(11)	NO	MUL	NULL	
goml_user_id	int(11)	NO	MUL	NULL	
goml_content	varchar(20)	NO		NULL	
goml_old_data	varchar(60)	YES		NULL	
goml_new_data	varchar(60)	YES		NULL	
goe_regdate	datetime	YES		NULL	
```
행 수: 0

### goods_sample
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
user_id	int(11)	NO	MUL	NULL	
category1	varchar(50)	NO		NULL	
category2	varchar(50)	NO		NULL	
category3	varchar(50)	NO		NULL	
```
행 수: 0

### goods_size_info
```sql
Field	Type	Null	Key	Default	Extra
gsi_no	int(11)	NO	PRI	NULL	auto_increment
gsi_user_id	int(11)	NO	MUL	NULL	
gsi_category	varchar(50)	NO		NULL	
gsi_set	tinyint(1)	NO		NULL	
gsi_set_item	varchar(50)	YES		NULL	
gsi_kr	varchar(255)	NO		NULL	
gsi_en	varchar(255)	NO		NULL	
gsi_use_yn	char(1)	NO		Y	
gsi_regdate	datetime	YES		NULL	
```
행 수: 32

### goods_size_modify_logs
```sql
Field	Type	Null	Key	Default	Extra
gsml_no	int(11)	NO	PRI	NULL	auto_increment
gsi_no	int(11)	NO	MUL	NULL	
gsml_user_id	int(11)	NO	MUL	NULL	
gsml_content	varchar(20)	NO		NULL	
gsml_old_data	varchar(255)	YES		NULL	
gsml_new_data	varchar(255)	YES		NULL	
gsml_regdate	datetime	YES		NULL	
```
행 수: 37

### goods_watermark_config
```sql
Field	Type	Null	Key	Default	Extra
WmcNo	int(11)	NO	PRI	NULL	auto_increment
user_id	int(11)	NO	MUL	NULL	
WmcOptionTitle1	varchar(50)	NO		NULL	
WmcOptionTitle2	varchar(50)	NO		NULL	
WmcOptionTitle3	varchar(50)	NO		NULL	
WmcOptionTitle4	varchar(50)	NO		NULL	
WmcOptionTitle5	varchar(50)	NO		NULL	
WmcIp	varchar(25)	NO		NULL	
created	datetime	NO		0000-00-00 00:00:00	
modified	timestamp	NO		current_timestamp()	on update current_timestamp()
```
행 수: 1

### goods_watermark_group
```sql
Field	Type	Null	Key	Default	Extra
GrpNo	int(11)	NO	PRI	NULL	auto_increment
user_id	int(11)	NO	MUL	NULL	
GrpKind	char(1)	NO		I	
GrpName	varchar(50)	NO		NULL	
GrpIp	varchar(25)	NO		NULL	
created	datetime	NO		0000-00-00 00:00:00	
modified	timestamp	NO		current_timestamp()	on update current_timestamp()
```
행 수: 31

### goods_watermark_icon
```sql
Field	Type	Null	Key	Default	Extra
WiNo	int(11)	NO	PRI	NULL	auto_increment
GrpNo	int(10) unsigned	NO		0	
user_id	int(11)	NO	MUL	NULL	
WiName	varchar(50)	NO		NULL	
WiFileName	varchar(100)	NO		NULL	
WiSetX	int(10) unsigned	NO		0	
WiSetY	int(10) unsigned	NO		0	
WiIp	varchar(25)	NO		NULL	
created	datetime	NO		0000-00-00 00:00:00	
modified	timestamp	NO		current_timestamp()	on update current_timestamp()
```
행 수: 13

### goods_watermark_icon_group
```sql
Field	Type	Null	Key	Default	Extra
GrpNo	int(11)	NO	PRI	NULL	auto_increment
user_id	int(11)	NO	MUL	NULL	
GrpName	varchar(50)	NO		NULL	
GrpIp	varchar(25)	NO		NULL	
created	datetime	NO		0000-00-00 00:00:00	
modified	timestamp	NO		current_timestamp()	on update current_timestamp()
```
행 수: 5

### goods_watermark_img_code
```sql
Field	Type	Null	Key	Default	Extra
WicNo	int(11)	NO	PRI	NULL	auto_increment
WicKey	varchar(20)	NO		NULL	
activated	tinyint(1) unsigned	NO		1	
created	datetime	NO		0000-00-00 00:00:00	
modified	timestamp	NO		current_timestamp()	on update current_timestamp()
```
행 수: 1

### goods_watermark_make
```sql
Field	Type	Null	Key	Default	Extra
WmmNo	int(11)	NO	PRI	NULL	auto_increment
user_id	int(11)	NO	MUL	NULL	
SetNo	int(10) unsigned	NO		0	
GdsId	int(10) unsigned	NO		0	
SetMakeFileName	varchar(100)	NO		NULL	
WmmIp	varchar(25)	NO		NULL	
created	datetime	NO		0000-00-00 00:00:00	
modified	timestamp	NO		current_timestamp()	on update current_timestamp()
```
행 수: 1022892

### goods_watermark_setting
```sql
Field	Type	Null	Key	Default	Extra
SetNo	int(11)	NO	PRI	NULL	auto_increment
GrpNo	int(11) unsigned	NO		0	
user_id	int(11)	NO	MUL	NULL	
SetName	varchar(50)	NO		NULL	
SetFrameFileName	varchar(100)	NO		NULL	
SetFrameWidth	smallint(4) unsigned	NO		0	
SetFrameHeight	smallint(4) unsigned	NO		0	
SetFrameRgb1	smallint(3) unsigned	NO		255	
SetFrameRgb2	smallint(3) unsigned	NO		255	
SetFrameRgb3	smallint(3) unsigned	NO		255	
SetMakeFileName	varchar(100)	NO		NULL	
SetIp	varchar(25)	NO		NULL	
created	datetime	NO		0000-00-00 00:00:00	
modified	timestamp	NO		current_timestamp()	on update current_timestamp()
```
행 수: 454

### goods_watermark_setting_extend
```sql
Field	Type	Null	Key	Default	Extra
WmSetNo	int(11)	NO	PRI	NULL	auto_increment
SetNo	int(11)	NO	MUL	NULL	
WmSetGb1	char(1)	NO		NULL	
WmSetGb2	smallint(4) unsigned	NO		NULL	
WmSetName	varchar(50)	NO		NULL	
WmSetX	int(10) unsigned	NO		0	
WmSetY	int(10) unsigned	NO		0	
WmSetFontName	varchar(50)	NO		NULL	
WmSetFontSize	tinyint(2) unsigned	NO		10	
WmSetFontRgb1	smallint(3) unsigned	NO		0	
WmSetFontRgb2	smallint(3) unsigned	NO		0	
WmSetFontRgb3	smallint(3) unsigned	NO		0	
created	datetime	NO		0000-00-00 00:00:00	
modified	timestamp	NO		current_timestamp()	on update current_timestamp()
```
행 수: 3309

### goods_wholesale_contract
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
user_id	int(11) unsigned	NO	MUL	0	
goods_id	int(11)	NO	UNI	NULL	
main_cnt	smallint(4) unsigned	NO		0	
model_cnt	smallint(4) unsigned	NO		0	
color_cnt	smallint(4) unsigned	NO		0	
main_price	int(10) unsigned	NO		0	
model_price	int(10) unsigned	NO		0	
color_price	int(10) unsigned	NO		0	
etc_price	int(10) unsigned	NO		0	
total_price	int(10) unsigned	NO		0	
etc_contents	text	YES		NULL	
created	datetime	NO		0000-00-00 00:00:00	
modified	timestamp	NO		current_timestamp()	on update current_timestamp()
GoodsCode	varchar(50)	YES		NULL	
GoodsEtc5	varchar(50)	YES		NULL	
BrandName	varchar(50)	YES		NULL	
optionColor	varchar(50)	YES		NULL	
GoodsEtc6	varchar(50)	NO		0	
numberPricePost	int(11)	YES		NULL	
status	varchar(55)	YES		NULL	
model_content	text	YES		NULL	
color_content	text	YES		NULL	
user_id_sale	varchar(255)	YES		NULL	
WholeSale_code	varchar(255)	YES		NULL	
StockingDate	date	YES		NULL	
modified_goods	timestamp	YES		NULL	
OptionSize	varchar(255)	YES		NULL	
memo	text	YES		NULL	
```
행 수: 43477

### goods_wish
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
user_id	int(11)	NO	MUL	NULL	
goods_id	int(11)	NO	MUL	NULL	
wishing	char(1)	NO	MUL	NULL	
wish_ip	varchar(25)	NO		NULL	
created	datetime	NO		0000-00-00 00:00:00	
modified	timestamp	NO		current_timestamp()	on update current_timestamp()
```
행 수: 334642

### market_goods_cate
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO		NULL	
market	char(1)	NO		NULL	
cate_json	longtext	NO		NULL	
created	datetime	NO		0000-00-00 00:00:00	
modified	timestamp	NO		current_timestamp()	on update current_timestamp()
```
행 수: 2

### market_goods_gosi
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
market	char(1)	NO	MUL	NULL	
grno	varchar(25)	NO		0	
grnm	varchar(100)	NO		NULL	
gosi_json	text	NO		NULL	
created	datetime	NO		0000-00-00 00:00:00	
modified	timestamp	NO		current_timestamp()	on update current_timestamp()
```
행 수: 50

### notice_category
```sql
Field	Type	Null	Key	Default	Extra
nc_no	int(11)	NO	PRI	NULL	auto_increment
nc_user_id	int(11)	NO	MUL	0	
nc_category_name	varchar(30)	NO		NULL	
nc_use_yn	char(1)	NO		Y	
nc_created	datetime	YES		0000-00-00 00:00:00	
```
행 수: 2

### notice_category_modify_logs
```sql
Field	Type	Null	Key	Default	Extra
ncml_no	int(11)	NO	PRI	NULL	auto_increment
ncml_user_id	int(11)	NO	MUL	0	
ncml_category_id	int(11)	NO	MUL	0	
ncml_modify_name	varchar(20)	NO		NULL	
ncml_old_data	text	YES		NULL	
ncml_modify_data	text	YES		NULL	
ncml_created	datetime	YES		0000-00-00 00:00:00	
```
행 수: 0

### order_barcode
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
barcode_upload_id	int(11)	NO	MUL	0	
goods_id	int(11)	NO	MUL	0	
barcode_num	varchar(20)	NO		NULL	
barcode_type	tinyint(1)	NO		1	
goods_name	varchar(255)	NO		NULL	
goods_option	varchar(50)	NO		NULL	
mixing_ratio	varchar(50)	YES		NULL	
option_size	varchar(50)	YES		NULL	
option_color	varchar(50)	YES		NULL	
country_name	varchar(20)	YES		NULL	
brand_name	varchar(20)	YES		NULL	
income_name	varchar(30)	YES		NULL	
seller_name	varchar(20)	YES		NULL	
address	varchar(200)	YES		NULL	
client_conselor_hp	varchar(13)	YES		NULL	
precautions	varchar(100)	YES		NULL	
make_date	varchar(10)	YES		NULL	
self_goodsCode	varchar(20)	YES	MUL		
print_count	int(10) unsigned	NO		0	
created	datetime	NO		0000-00-00 00:00:00	
```
행 수: 387037

### order_barcode_upload
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
user_id	int(11)	NO	MUL	0	
file_name	varchar(50)	NO		NULL	
barcode_type	tinyint(1)	NO		1	
created	datetime	NO		0000-00-00 00:00:00	
```
행 수: 3793

### order_block
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
user_id	int(11)	NO	MUL	0	
arrival_user_id	int(11)	NO	MUL	0	
order_file_name	varchar(50)	NO		NULL	
arrival_file_name	varchar(50)	YES		NULL	
order_shop_name	varchar(50)	NO		NULL	
order_store_quantity	int(10) unsigned	NO		0	
order_tot_quantity	int(10) unsigned	NO		0	
order_tot_price	int(10) unsigned	YES		NULL	
order_username	varchar(20)	NO		NULL	
order_user_tel	varchar(13)	NO		NULL	
status	tinyint(1)	NO	MUL	0	
created	datetime	NO	MUL	0000-00-00 00:00:00	
complate_date	datetime	YES		NULL	
cancel_date	datetime	YES		NULL	
arrival_date	datetime	YES		NULL	
arrival_reset_date	datetime	YES		NULL	
same_file_cnt	varchar(5)	NO			
arrival_same_file_cnt	varchar(5)	YES		NULL	
```
행 수: 937

### order_block_alimTalk_logs
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
user_id	int(11)	NO	MUL	0	
order_id	int(11)	NO	MUL	0	
success_yn	char(1)	NO		Y	
created	datetime	NO		0000-00-00 00:00:00	
```
행 수: 927

### order_block_detail
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
order_id	int(11)	NO	MUL	0	
arrival_id	int(11)	YES	MUL	0	
store_id	int(11)	NO	MUL	0	
store_shop_name	varchar(30)	NO		NULL	
store_name	varchar(30)	YES		NULL	
store_tel	varchar(13)	NO		NULL	
store_addr	varchar(200)	NO		NULL	
goods_id	int(11)	NO	MUL	0	
goods_code	varchar(20)	NO	MUL	NULL	
goods_barcode	varchar(20)	YES		NULL	
goods_name	varchar(255)	YES	MUL	NULL	
goods_model	varchar(50)	YES		NULL	
goods_option	varchar(50)	YES		NULL	
original_code	varchar(20)	NO	MUL	NULL	
order_parcel_id	int(11)	NO	MUL	0	
order_quantity	int(10) unsigned	NO		0	
order_cost	int(10) unsigned	NO		0	
arrival_tot_quantity	int(10)	NO		0	
order_parcel_price	int(10) unsigned	YES		NULL	
real_quantity	int(10) unsigned	YES		NULL	
order_price	int(10) unsigned	YES		NULL	
order_status	tinyint(1)	NO		1	
release_date	datetime	YES		NULL	
norelease_memo	text	YES		NULL	
norelease_date	varchar(20)	YES		NULL	
norelease_type	tinyint(1)	YES		NULL	
arrival	int(10) unsigned	YES		NULL	
defective	int(10) unsigned	YES		NULL	
arrival_price	int(10) unsigned	YES		NULL	
status_date	datetime	YES		NULL	
```
행 수: 494932

### order_block_modify_logs
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
order_detail_id	int(11)	NO	MUL	0	
modify_user_id	int(11)	NO	MUL	0	
column_name	varchar(30)	NO		NULL	
old_data	varchar(200)	YES		NULL	
modify_data	varchar(200)	YES		NULL	
created	datetime	NO		0000-00-00 00:00:00	
```
행 수: 14

### order_block_new
```sql
Field	Type	Null	Key	Default	Extra
ob_no	int(11)	NO	PRI	NULL	auto_increment
od_no	int(11)	NO	MUL	NULL	
ob_file_name	varchar(100)	NO		NULL	
```
행 수: 832

### order_norelease_modify_logs
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
order_detail_id	int(11)	NO	MUL	0	
modify_user_id	int(11)	NO	MUL	0	
column_name	varchar(30)	NO		NULL	
old_cost	int(10) unsigned	YES		NULL	
new_cost	int(10) unsigned	YES		NULL	
old_type	tinyint(1)	YES		NULL	
new_type	tinyint(1)	YES		NULL	
old_date	tinyint(1)	YES		NULL	
new_date	tinyint(1)	YES		NULL	
old_memo	text	YES		NULL	
new_memo	text	YES		NULL	
created	datetime	NO		0000-00-00 00:00:00	
use_yn	char(1)	NO		Y	
```
행 수: 56401

### order_product
```sql
Field	Type	Null	Key	Default	Extra
op_no	int(11)	NO	PRI	NULL	auto_increment
od_no	int(11)	YES	MUL	NULL	
ar_no	int(11)	YES	MUL	NULL	
op_store_id	int(11)	NO	MUL	NULL	
op_pickman_id	int(11)	YES	MUL	NULL	
op_status	varchar(10)	NO	MUL	1-1	
op_goods_id	int(11)	NO	MUL	0	
op_goods_code	varchar(20)	NO	MUL	NULL	
op_goods_barcode	varchar(20)	YES	MUL	NULL	
op_goods_name	varchar(255)	YES	MUL	NULL	
op_goods_model	varchar(255)	YES	MUL	NULL	
op_goods_option	varchar(50)	YES		NULL	
op_original_code	varchar(50)	YES	MUL	NULL	
op_order_cnt	int(10) unsigned	NO		NULL	
op_order_cost	int(10) unsigned	NO		NULL	
op_order_price	int(10) unsigned	NO		NULL	
op_release_cnt	int(10) unsigned	YES		NULL	
op_release_cost	int(10) unsigned	YES		NULL	
op_release_price	int(10) unsigned	YES		NULL	
op_norelease_reason	tinyint(1)	YES		NULL	
op_norelease_memo	text	YES		NULL	
op_release_duedate	varchar(20)	YES		NULL	
op_arrival_error	char(1)	NO		N	
op_arrival_cnt	int(10) unsigned	YES		NULL	
op_arrival_price	int(10) unsigned	YES		NULL	
op_defective_cnt	int(10) unsigned	YES		NULL	
op_defective_price	int(10) unsigned	YES		NULL	
op_regdate	datetime	YES		NULL	
```
행 수: 368983

### order_product_box
```sql
Field	Type	Null	Key	Default	Extra
opb_no	int(11)	NO	PRI	NULL	auto_increment
od_no	int(11)	NO	MUL	NULL	
store_no	int(11)	NO	MUL	NULL	
opb_cnt	smallint(6)	NO		1	
```
행 수: 70529

### order_product_status
```sql
Field	Type	Null	Key	Default	Extra
ops_no	int(11)	NO	PRI	NULL	auto_increment
op_no	int(11)	NO	MUL	NULL	
ops_user_id	int(11)	NO	MUL	NULL	
ops_ip	varchar(40)	YES		NULL	
ops_code	varchar(10)	NO		NULL	
ops_name	varchar(40)	NO		NULL	
ops_regdate	datetime	YES		NULL	
```
행 수: 377865

### order_request
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
order_id	int(11)	NO	MUL	0	
receiver_id	int(11)	NO	MUL	0	
store_id	int(11)	NO	MUL	0	
receiver_username	varchar(20)	NO		NULL	
receiver_shop_tel	varchar(13)	NO		NULL	
receiver_shop_hp	varchar(13)	NO		NULL	
store_username	varchar(20)	NO		NULL	
store_shop_tel	varchar(13)	NO		NULL	
store_shop_hp	varchar(13)	NO		NULL	
store_shop_addr	varchar(100)	NO		NULL	
send_parcel_2	int(11)	NO	MUL	0	
send_parcel_2_confirm	datetime	YES		NULL	
send_parcel_3	int(11)	YES	MUL	NULL	
send_parcel_3_confirm	datetime	YES		NULL	
send_status	tinyint(1)	NO	MUL	1	
box_cnt	int(11)	YES		NULL	
created	datetime	NO		0000-00-00 00:00:00	
```
행 수: 88597

### order_search_logs
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
user_id	int(11)	NO	MUL	0	
content	varchar(50)	NO		NULL	
view_yn	char(1)	NO	MUL	Y	
search_type	varchar(20)	NO		NULL	
created	datetime	NO		0000-00-00 00:00:00	
```
행 수: 87

### order_store_check_logs
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
store_id	int(11)	NO	MUL	0	
order_id	int(11)	NO	MUL	0	
update_date	datetime	YES		NULL	
created	datetime	NO		0000-00-00 00:00:00	
```
행 수: 78968

### ordered_items
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
order_id	varchar(255)	NO		NULL	
item_id	int(11)	NO		NULL	
old_price	float	NO		NULL	
quantity	int(11)	NO		NULL	
```
행 수: 2

### orders
```sql
Field	Type	Null	Key	Default	Extra
od_no	int(11)	NO	PRI	NULL	auto_increment
od_user_id	int(11)	NO	MUL	NULL	
od_type	tinyint(1)	NO		1	
od_store_cnt	int(10) unsigned	NO		NULL	
od_price	int(10) unsigned	NO		NULL	
od_product_cnt	int(10) unsigned	NO		NULL	
od_status	tinyint(4)	NO		1	
od_regdate	datetime	YES		NULL	
order_block_no	int(11)	NO		NULL	
```
행 수: 780

### orders_old
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
confirmed	tinyint(1)	NO		0	
order_id	varchar(255)	NO		NULL	
user_id	int(11)	YES		NULL	
name	varchar(255)	NO		NULL	
email	varchar(255)	NO		NULL	
telephone	varchar(255)	NO		NULL	
address	text	NO		NULL	
sum	double	NO		NULL	
date	timestamp	NO		current_timestamp()	
```
행 수: 1

### pickup_delivery_kind
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
delivery_name	varchar(30)	NO		NULL	
real_name	varchar(30)	NO		NULL	
use_yn	char(1)	NO		Y	
```
행 수: 9

### pickup_delivery_kind_set
```sql
Field	Type	Null	Key	Default	Extra
parcel_gb	int(11)	NO	PRI	NULL	
```
행 수: 1

### pickup_delivery_package
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
delivery_id	int(11)	NO	MUL	0	
package_name	varchar(20)	NO		NULL	
package_info	varchar(100)	NO		NULL	
```
행 수: 25

### pigup_delivery_setting
```sql
Field	Type	Null	Key	Default	Extra
PdsNo	int(11)	NO	PRI	NULL	auto_increment
user_id	int(11)	NO	MUL	NULL	
PdsNextDayPrice	smallint(4) unsigned	NO		0	
PdsTheDayPrice	smallint(4) unsigned	NO		0	
PdsRemotePlacePrice	smallint(4) unsigned	NO		0	
PdsDepositBankInfo	varchar(100)	NO		NULL	
PdsIp	varchar(25)	NO		NULL	
created	datetime	NO		0000-00-00 00:00:00	
```
행 수: 2

### pigup_order
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
goods_id	int(11) unsigned	NO		0	
send_id	int(11) unsigned	NO	MUL	0	
receiver_id	int(10) unsigned	NO	MUL	0	
receiver_username	varchar(20)	NO		NULL	
receiver_shop_name	varchar(30)	NO		NULL	
receiver_shop_addr	varchar(50)	NO		NULL	
receiver_shop_tel	varchar(13)	NO		NULL	
receiver_shop_hp	varchar(13)	NO		NULL	
send_username	varchar(20)	NO		NULL	
send_shop_name	varchar(30)	NO		NULL	
send_shop_addr	varchar(50)	NO		NULL	
send_shop_tel	varchar(13)	NO		NULL	
send_shop_hp	varchar(13)	NO		NULL	
send_parcel_gb	char(1)	NO		1	
send_parcel	int(6)	NO		0	
send_payment	char(1)	NO		2	
order_goods_price	int(10)	NO		0	
order_total_price	int(10) unsigned	NO		0	
order_total_cnt	smallint(4)	NO		0	
order_option_info	text	NO		NULL	
send_total_price	int(10) unsigned	NO		0	
send_total_cnt	smallint(4) unsigned	NO		0	
send_option_info	text	NO		NULL	
goods_info	text	NO		NULL	
state	char(1)	NO	MUL	1	
created	datetime	NO		0000-00-00 00:00:00	
modified	timestamp	NO		current_timestamp()	
```
행 수: 24

### temp_user_profiles
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
register_id	int(11)	NO		NULL	
shop_gb	varchar(20)	NO		shop	
website	varchar(100)	NO			
shop_name	varchar(50)	NO		NULL	
shop_zip1	char(5)	NO		NULL	
shop_addr1	varchar(50)	NO		NULL	
shop_addr2	varchar(50)	NO		NULL	
shop_addr3	varchar(50)	NO			
shop_addr4	varchar(50)	NO			
shopping_center	smallint(5) unsigned	NO		0	
shopping_center_floor	varchar(5)	NO		0	
shopping_center_number	varchar(10)	NO		0	
business_name	varchar(20)	NO			
shop_num	varchar(50)	NO		0	
shop_tel	varchar(20)	NO		00-0000-0000	
shop_staff_hp	varchar(20)	NO		000-0000-0000	
shop_show_hp	varchar(20)	NO		000-0000-0000	
kakao_id	varchar(30)	NO			
shop_taxid	varchar(20)	NO		000-0000-000	
shop_taxid_copy	varchar(50)	NO			
shop_logo	varchar(50)	NO			
delegate_name	varchar(20)	NO			
delegate_hp	varchar(20)	NO		000-0000-0000	
office_tel	varchar(20)	NO		00-0000-0000	
office_zip	char(5)	NO		00000	
office_addr1	varchar(50)	NO			
office_addr2	varchar(50)	NO			
office_addr3	varchar(50)	NO			
office_addr4	varchar(50)	NO			
shop_addr	varchar(200)	NO			
shop_account	varchar(100)	NO			
shop_bank	varchar(50)	NO			
shop_goods_new_cnt	tinyint(3) unsigned	NO		0	
shop_kapl_url	varchar(100)	NO			
sale_gb	varchar(50)	NO			
sale_form	varchar(50)	NO			
target_style	smallint(5) unsigned	NO		0	
target_age	smallint(5) unsigned	NO		0	
shop_concept	smallint(5) unsigned	NO		0	
target_sex	smallint(5) unsigned	NO		0	
etc_memo	varchar(4000)	NO			
```
행 수: 24

### user_apikey
```sql
Field	Type	Null	Key	Default	Extra
key_id	char(32)	NO	PRI	NULL	
user_id	int(11)	NO	PRI	0	
key_ip	varchar(40)	NO		NULL	
last_date	timestamp	NO		current_timestamp()	on update current_timestamp()
```
행 수: 4

### user_autologin
```sql
Field	Type	Null	Key	Default	Extra
key_id	char(32)	NO	PRI	NULL	
user_id	int(11)	NO	PRI	0	
user_agent	varchar(150)	NO		NULL	
last_ip	varchar(40)	NO		NULL	
last_login	timestamp	NO		current_timestamp()	on update current_timestamp()
```
행 수: 294

### user_client
```sql
Field	Type	Null	Key	Default	Extra
client_id	int(11)	NO	PRI	NULL	auto_increment
shop_name	varchar(50)	NO		NULL	
delegate_name	varchar(20)	NO		NULL	
shop_zip1	char(5)	YES		NULL	
shop_addr1	varchar(50)	YES		NULL	
shop_addr2	varchar(50)	YES		NULL	
shopping_center	smallint(4)	YES		0	
shopping_center_floor	varchar(5)	YES		NULL	
shopping_center_number	varchar(10)	YES		NULL	
shop_staff_hp	varchar(20)	NO		NULL	
shop_tel	varchar(20)	NO		NULL	
etc_memo	text	YES		NULL	
registerdby	int(11)	NO		NULL	
```
행 수: 2

### user_company_match
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
userid	int(11)	NO	MUL	NULL	
profileid	int(11)	NO		NULL	
registerdyn	int(11)	NO		NULL	
```
행 수: 36651

### user_delivery_partner
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
user_id	int(11)	NO		NULL	
dp_info	varchar(50)	NO		NULL	
dp_name	varchar(50)	NO		NULL	
dp_zip	varchar(5)	NO		NULL	
dp_addr1	varchar(50)	NO		NULL	
dp_addr2	varchar(50)	NO		NULL	
dp_addr3	varchar(100)	NO		NULL	
dp_addr4	varchar(100)	NO		NULL	
dp_phone	char(13)	NO		NULL	
dp_hphone	char(13)	NO		NULL	
dp_etc	text	YES		NULL	
created	datetime	NO		0000-00-00 00:00:00	
modified	timestamp	NO		current_timestamp()	on update current_timestamp()
dp_user_id	int(11)	NO		NULL	
dp_status	tinyint(1)	NO		NULL	
```
행 수: 16

### user_deposit
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
user_id	int(11)	NO	MUL	NULL	
price	int(11)	NO		0	
real_price	int(10) unsigned	NO		0	
balance	int(11)	NO		0	
pay_method	varchar(20)	YES		NULL	
depositor	varchar(20)	NO		NULL	
memo	varchar(255)	NO		NULL	
kind	char(1)	NO	MUL	P	
kind_m_gb	char(1)	YES		NULL	
state	char(1)	NO	MUL	N	
left_deposit	int(11)	YES		NULL	
state_date	datetime	NO		0000-00-00 00:00:00	
created	datetime	NO		0000-00-00 00:00:00	
phone	varchar(30)	YES		NULL	
order_no	varchar(100)	YES		NULL	
imp_uid	varchar(255)	YES		NULL	
merchant_uid	varchar(200)	YES		NULL	
path	varchar(200)	YES		NULL	
cancel_date	datetime	YES		NULL	
popbill_tid	varchar(50)	YES		NULL	
```
행 수: 104624

### user_deposit_pg
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
user_id	int(11)	NO	MUL	NULL	
prdt_nm	varchar(255)	NO		NULL	
prdt_no	varchar(255)	YES		NULL	
prdt_kind	varchar(255)	YES		NULL	
price	int(11)	NO		NULL	
imp_uid	varchar(255)	YES		NULL	
merchant_uid	varchar(255)	YES		NULL	
success_yn	char(1)	YES		N	
created	datetime	YES		current_timestamp()	
```
행 수: 36

### user_down_service
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
deposit_id	int(11) unsigned	NO		0	
user_id	int(11)	NO		NULL	
service_name	varchar(50)	NO		NULL	
service_price	int(11) unsigned	NO		0	
down_cnt	varchar(4)	NO		0	
discount_rate	varchar(2)	NO		0	
settlement_fund	mediumint(6) unsigned	NO		0	
created	datetime	NO		0000-00-00 00:00:00	
```
행 수: 2888

### user_employee
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
user_id	int(11)	YES		NULL	
emp_id	varchar(50)	NO		NULL	
emp_pw	varchar(255)	NO		NULL	
emp_pos	varchar(50)	YES		NULL	
emp_nm	varchar(50)	YES		NULL	
emp_hp	varchar(20)	YES		NULL	
```
행 수: 6

### user_freelancer
```sql
Field	Type	Null	Key	Default	Extra
id	int(10) unsigned	NO	PRI	NULL	auto_increment
userId	varchar(50)	YES		NULL	
Type	varchar(50)	YES		NULL	
Classification	varchar(50)	YES		NULL	
Name	varchar(50)	YES		NULL	
RRN	varchar(50)	YES		NULL	
PhoneNumber	varchar(50)	YES		NULL	
Email	varchar(50)	YES		NULL	
Address	varchar(50)	YES		NULL	
PayInfo	varchar(50)	YES		NULL	
BankName	varchar(50)	YES		NULL	
AccountNumber	varchar(255)	YES		NULL	
AccountImage	varchar(50)	YES		NULL	
IdcardImage	varchar(50)	YES		NULL	
PortfolioImage	text	YES		NULL	
PortfolioURL	varchar(50)	YES		NULL	
Created	datetime	YES		NULL	
```
행 수: 33

### user_id_update_logs
```sql
Field	Type	Null	Key	Default	Extra
uiu_no	int(11)	NO	PRI	NULL	auto_increment
uiu_user_id	int(11)	NO	MUL	0	
uiu_user_index	int(11)	NO	MUL	0	
uiu_old_user_id	varchar(40)	YES		NULL	
uiu_new_user_id	varchar(40)	YES		NULL	
uiu_created	datetime	YES		0000-00-00 00:00:00	
```
행 수: 40

### user_login_log
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
user_id	int(11)	NO		NULL	
login_ip	varchar(40)	YES		NULL	
login_page	varchar(20)	YES		login	
created	datetime	NO		0000-00-00 00:00:00	
```
행 수: 238352

### user_manager
```sql
Field	Type	Null	Key	Default	Extra
id	int(10) unsigned	NO	PRI	NULL	auto_increment
userImage	varchar(50)	YES		NULL	
userId	varchar(50)	YES		NULL	
userName	varchar(50)	YES		NULL	
userDepartment	varchar(50)	YES		NULL	
userTask	varchar(50)	YES		NULL	
userTel1	varchar(50)	YES		NULL	
userEmail	varchar(50)	YES		NULL	
UserStartDay	datetime	YES		NULL	
UserEndtDay	datetime	YES		NULL	
State	varchar(50)	YES		NULL	
userTel2	varchar(50)	YES		NULL	
userAuth	varchar(50)	YES		NULL	
created	datetime	YES		NULL	
```
행 수: 48

### user_manual_log
```sql
Field	Type	Null	Key	Default	Extra
uml_id	int(11)	NO	PRI	NULL	auto_increment
uml_user_id	int(11)	NO		NULL	
uml_manual	varchar(50)	NO		NULL	
uml_cnt	int(11)	NO		1	
uml_update	datetime	YES		NULL	
uml_regdate	datetime	YES		NULL	
```
행 수: 340

### user_market
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
user_id	int(11)	NO	MUL	NULL	
market	char(1)	NO	MUL	NULL	
market_id	varchar(50)	NO		NULL	
market_pw	varchar(50)	NO		NULL	
activated	tinyint(1) unsigned	NO		0	
created	datetime	NO		0000-00-00 00:00:00	
modified	timestamp	NO		current_timestamp()	on update current_timestamp()
```
행 수: 33

### user_market_info
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
user_id	int(11)	NO	MUL	NULL	
market	char(1)	NO	MUL	NULL	
DeliveryJson	text	NO		NULL	
created	datetime	NO		0000-00-00 00:00:00	
modified	timestamp	NO		current_timestamp()	on update current_timestamp()
```
행 수: 5

### user_model
```sql
Field	Type	Null	Key	Default	Extra
id	int(11) unsigned	NO	PRI	NULL	auto_increment
name	varchar(255)	YES		NULL	
RRN	varchar(255)	YES		NULL	
phoneNumber	varchar(255)	YES		NULL	
email	varchar(255)	YES		NULL	
address	varchar(255)	YES		NULL	
payInfo	varchar(255)	YES		NULL	
bankName	varchar(255)	YES		NULL	
accountNumber	varchar(50)	YES		NULL	
accountImage	varchar(255)	YES		NULL	
idcardImage	varchar(255)	YES		NULL	
contactImage	varchar(255)	YES		NULL	
portfolioImage	varchar(255)	YES		NULL	
modelImages	text	YES		NULL	
size	varchar(255)	YES		NULL	
doneAll	varchar(255)	YES		NULL	
doneWeek	varchar(255)	YES		NULL	
notdoneNow	varchar(255)	YES		NULL	
created	datetime	YES		NULL	
```
행 수: 36

### user_msg
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
user_id	int(11)	NO		NULL	
title	varchar(255)	NO		NULL	
message	text	NO		NULL	
send_for	int(11)	NO		NULL	
createdAt	timestamp	NO		current_timestamp()	
read_yn	char(1)	NO		N	
```
행 수: 1485932

### user_msg_aligo
```sql
Field	Type	Null	Key	Default	Extra
uma_seq	int(11)	NO	PRI	NULL	auto_increment
uma_method	char(1)	YES		NULL	
uma_send_id	int(11)	NO	MUL	NULL	
uma_send_nm	varchar(50)	NO		NULL	
uma_recv_hp	varchar(20)	NO		NULL	
uma_recv_nm	varchar(50)	NO		NULL	
uma_subject	varchar(100)	NO		NULL	
uma_message	varchar(4000)	NO		NULL	
uma_time_type	char(1)	NO		1	
uma_rsrv_date	varchar(20)	YES		NULL	
uma_send_date	varchar(20)	YES		NULL	
uma_sms_type	varchar(10)	YES		NULL	
uma_group_id	int(11)	YES		NULL	
uma_group_name	varchar(50)	YES		NULL	
uma_templt_code	varchar(50)	YES		NULL	
uma_price	int(11)	NO		NULL	
uma_result	char(1)	YES		P	
uma_result_mid	int(11)	YES		NULL	
uma_result_msg	varchar(100)	YES		NULL	
uma_reg_date	datetime	YES		current_timestamp()	
```
행 수: 78658

### user_partner
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
user_id	int(11)	NO		NULL	
partner_id	int(11)	NO		NULL	
created	datetime	NO		NULL	
```
행 수: 25

### user_partner_match
```sql
Field	Type	Null	Key	Default	Extra
user_id	int(11)	NO	PRI	NULL	
partner_id	int(11)	NO	PRI	NULL	
reg_date	datetime	YES		current_timestamp()	
```
행 수: 101403

### user_pay
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
user_id	int(11)	NO		NULL	
price	int(11) unsigned	NO		0	
depositor	varchar(20)	NO		NULL	
memo	varchar(255)	NO		NULL	
kind	char(1)	NO		1	
created	datetime	NO		0000-00-00 00:00:00	
```
행 수: 0

### user_place
```sql
Field	Type	Null	Key	Default	Extra
id	int(10) unsigned	NO	PRI	NULL	auto_increment
Name	varchar(255)	YES		NULL	
Tel1	varchar(255)	YES		NULL	
Tel2	varchar(255)	YES		NULL	
Email	varchar(255)	YES		NULL	
Address	varchar(255)	YES		NULL	
Costbase	varchar(255)	YES		NULL	
CosAdd	varchar(255)	YES		NULL	
BankName	varchar(255)	YES		NULL	
AccountNumber	varchar(255)	YES		NULL	
AccountImage	varchar(255)	YES		NULL	
BisinessRegistration	varchar(255)	YES		NULL	
EtcNote	varchar(255)	YES		NULL	
SpacePhoto	text	YES		NULL	
Website	varchar(255)	YES		NULL	
created	datetime	YES		NULL	
```
행 수: 90

### user_popup_list
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
user_id	int(11)	NO	MUL	0	
pop_id	int(11)	NO	MUL	NULL	
cycle_yn	char(1)	NO		N	
created	datetime	NO		0000-00-00 00:00:00	
update_time	datetime	NO		0000-00-00 00:00:00	
```
행 수: 9679

### user_profiles
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
user_id	int(11)	NO	UNI	NULL	
shop_gb	varchar(20)	NO		shop	
website	varchar(100)	YES		NULL	
shop_name	varchar(50)	NO		NULL	
shop_zip1	char(5)	YES		NULL	
shop_addr1	varchar(50)	YES		NULL	
shop_addr2	varchar(50)	YES		NULL	
shop_addr3	varchar(50)	YES		NULL	
shop_addr4	varchar(50)	YES		NULL	
shopping_center	smallint(4) unsigned	NO		0	
shopping_center_floor	varchar(5)	YES		NULL	
shopping_center_number	varchar(10)	YES		NULL	
business_name	varchar(20)	YES		NULL	
shop_num	varchar(50)	YES		NULL	
shop_tel	varchar(20)	YES		NULL	
shop_staff_hp	varchar(20)	YES		NULL	
shop_show_hp	varchar(20)	YES		NULL	
kakao_id	varchar(30)	YES		NULL	
kakao_link_url	varchar(100)	YES		NULL	
shop_taxid	varchar(20)	YES		NULL	
shop_taxid_copy	varchar(50)	YES		NULL	
shop_logo	varchar(50)	YES		NULL	
delegate_name	varchar(20)	YES		NULL	
shop_staff_name	varchar(50)	YES		NULL	
delegate_hp	varchar(20)	YES		NULL	
office_tel	varchar(20)	YES		NULL	
office_zip	char(5)	YES		NULL	
office_addr1	varchar(50)	YES		NULL	
office_addr2	varchar(50)	YES		NULL	
office_addr3	varchar(50)	YES		NULL	
office_addr4	varchar(50)	YES		NULL	
shop_addr	varchar(200)	YES		NULL	
shop_account	varchar(100)	YES		NULL	
shop_account_name	varchar(100)	YES		NULL	
shop_bank	varchar(50)	YES		NULL	
shop_goods_new_cnt	tinyint(2) unsigned	NO		0	
shop_kapl_url	varchar(100)	YES		NULL	
sale_gb	varchar(50)	YES		NULL	
sale_form	varchar(50)	YES		NULL	
target_style	varchar(50)	YES		NULL	
target_age	varchar(50)	YES		NULL	
shop_concept	varchar(50)	YES		NULL	
target_sex	varchar(50)	YES		NULL	
mall_new_item_list_type	char(1)	NO		A	
etc_memo	text	YES		NULL	
registerdby	int(11)	NO		0	
mall_login_used	char(1)	NO		N	
man_read_yn	char(1)	NO		N	
shop_naver_meta	varchar(250)	YES		NULL	
shop_description	text	YES		NULL	
shop_google_meta	varchar(250)	YES		NULL	
shop_title_meta	varchar(250)	YES		NULL	
shop_wechat_id	varchar(250)	YES		NULL	
shop_instagram_id	varchar(250)	YES		NULL	
shop_new_items_pc	varchar(10)	YES		NULL	
shop_new_items_mobile	varchar(10)	YES		NULL	
shop_best_items_pc	varchar(10)	YES		NULL	
shop_best_items_mobile	varchar(10)	YES		NULL	
```
행 수: 79415

### user_profiles_2109012314
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
user_id	int(11)	NO	UNI	NULL	
shop_gb	varchar(20)	NO		shop	
website	varchar(100)	NO		NULL	
shop_name	varchar(50)	NO		NULL	
shop_zip1	char(5)	YES		NULL	
shop_addr1	varchar(50)	YES		NULL	
shop_addr2	varchar(50)	YES		NULL	
shop_addr3	varchar(50)	YES		NULL	
shop_addr4	varchar(50)	YES		NULL	
shopping_center	smallint(4) unsigned	NO		0	
shopping_center_floor	varchar(5)	NO		NULL	
shopping_center_number	varchar(10)	NO		NULL	
business_name	varchar(20)	NO		NULL	
shop_num	varchar(50)	NO		NULL	
shop_tel	varchar(20)	NO		NULL	
shop_staff_hp	varchar(20)	NO		NULL	
shop_show_hp	varchar(20)	NO		NULL	
kakao_id	varchar(30)	NO		NULL	
kakao_link_url	varchar(100)	NO		NULL	
shop_taxid	varchar(20)	NO		NULL	
shop_taxid_copy	varchar(50)	NO		NULL	
shop_logo	varchar(50)	NO		NULL	
delegate_name	varchar(20)	NO		NULL	
delegate_hp	varchar(20)	NO		NULL	
office_tel	varchar(20)	NO		NULL	
office_zip	char(5)	NO		NULL	
office_addr1	varchar(50)	NO		NULL	
office_addr2	varchar(50)	NO		NULL	
office_addr3	varchar(50)	NO		NULL	
office_addr4	varchar(50)	NO		NULL	
shop_addr	varchar(200)	NO		NULL	
shop_account	varchar(100)	NO		NULL	
shop_account_name	varchar(100)	NO		NULL	
shop_bank	varchar(50)	NO		NULL	
shop_goods_new_cnt	tinyint(2) unsigned	NO		0	
shop_kapl_url	varchar(100)	NO		NULL	
sale_gb	varchar(50)	NO		NULL	
sale_form	varchar(50)	NO		NULL	
target_style	varchar(50)	NO		NULL	
target_age	varchar(50)	NO		NULL	
shop_concept	varchar(50)	NO		NULL	
target_sex	varchar(50)	NO		NULL	
mall_new_item_list_type	char(1)	NO		A	
etc_memo	text	NO		NULL	
registerdby	int(11)	NO		0	
```
행 수: 5961

### user_qna_group
```sql
Field	Type	Null	Key	Default	Extra
gid	int(10) unsigned	NO	PRI	NULL	auto_increment
uid_mst	int(10) unsigned	NO		NULL	
uid_gst	int(10) unsigned	NO		NULL	
```
행 수: 881

### user_qna_msg
```sql
Field	Type	Null	Key	Default	Extra
cid	int(10) unsigned	NO	PRI	NULL	auto_increment
gid	int(10) unsigned	NO	MUL	NULL	
uid	int(10) unsigned	NO		NULL	
msg	varchar(255)	NO		NULL	
read_yn	char(1)	YES		N	
del_yn	char(1)	YES		N	
reg_dt	varchar(10)	YES		NULL	
```
행 수: 314

### user_sns
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
user_id	int(11)	NO	MUL	NULL	
sns_gb	char(1)	NO	MUL	NULL	
sns_id	varchar(50)	NO		NULL	
sns_pw	varchar(50)	NO		NULL	
sns_key	varchar(40)	NO		NULL	
app_name	varchar(20)	NO		NULL	
activated	tinyint(1) unsigned	NO		0	
created	datetime	NO		0000-00-00 00:00:00	
modified	timestamp	NO		current_timestamp()	on update current_timestamp()
```
행 수: 8

### user_store_bookmark
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
user_id	int(11)	NO	MUL	NULL	
store_id	int(11)	NO	MUL	NULL	
ip	varchar(25)	NO		NULL	
created	datetime	NO		0000-00-00 00:00:00	
```
행 수: 15

### user_template_msg
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
user_id	int(11)	NO		NULL	
message	text	NO		NULL	
```
행 수: 32

### user_unregister_reason
```sql
Field	Type	Null	Key	Default	Extra
users_id	int(11)	NO		NULL	
reason_yn01	char(1)	YES		N	
reason_yn02	char(1)	YES		N	
reason_yn03	char(1)	YES		N	
reason_yn04	char(1)	YES		N	
reason_etc	char(1)	YES		N	
reason_etc_desc	varchar(4000)	YES		NULL	
reg_dt	datetime	YES		current_timestamp()	
```
행 수: 66

### user_wholeSale_log
```sql
Field	Type	Null	Key	Default	Extra
id	int(11) unsigned	NO	PRI	NULL	auto_increment
wholesale_code	varchar(255)	YES		NULL	
wholesale_id	int(11)	YES		NULL	
user_id	int(11)	YES		NULL	
startDate	date	YES		NULL	
endDate	date	YES		NULL	
number_product	int(11)	YES		NULL	
modified	timestamp	YES		NULL	
```
행 수: 555

### user_wholesale_charge
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
user_id	int(11)	NO	MUL	NULL	
month_price	int(10) unsigned	NO		0	
total_main_cnt	smallint(4) unsigned	NO		0	
total_model_cnt	smallint(4) unsigned	NO		0	
total_color_cnt	smallint(4) unsigned	NO		0	
total_main_price	int(10) unsigned	NO		0	
total_model_price	int(10) unsigned	NO		0	
total_color_price	int(10) unsigned	NO		0	
total_etc_price	int(10) unsigned	NO		0	
total_add_price	int(10) unsigned	NO		0	
total_price_sum	int(10) unsigned	NO		0	
charge_goods_cnt	smallint(3) unsigned	NO		0	
charge_date	char(7)	NO	MUL	0000-00	
change_alarm_cnt	tinyint(2) unsigned	NO		0	
change_state	char(1)	NO		N	
change_way	char(1)	NO		M	
depositor	varchar(20)	YES		NULL	
created	datetime	NO		0000-00-00 00:00:00	
modified	datetime	NO		current_timestamp()	on update current_timestamp()
contract_date_start	date	YES		NULL	
goods_create_num	smallint(3)	YES		NULL	
model_add_price	mediumint(3)	YES		NULL	
color_add_price	mediumint(3)	YES		NULL	
add_goods_price	mediumint(3)	YES		NULL	
add_model_price	mediumint(3)	YES		NULL	
add_color_price	mediumint(3)	YES		NULL	
etc_add_price	mediumint(3)	YES		NULL	
charge_process	varchar(55)	YES		NULL	
notPaid	varchar(50)	YES		NULL	
contract_code	varchar(50)	YES	MUL	NULL	
status	varchar(255)	YES		NULL	
month_price_popup	varchar(55)	YES		NULL	
additionalCharge	varchar(55)	YES		NULL	
totalModelPrice	varchar(55)	YES		NULL	
totalColorPrice	varchar(55)	YES		NULL	
oldPrice	varchar(55)	YES		NULL	
numberPrice	varchar(55)	YES		NULL	
total_price_popup	varchar(55)	YES		NULL	
changeSubmitDate	datetime	YES		NULL	
billingCompletion_date	datetime	YES		NULL	
depositCompleted_date	datetime	YES		NULL	
type_change_status	tinyint(1)	YES		1	
total_billing_vat	varchar(55)	YES		0	
memo	text	YES		NULL	
difference	varchar(55)	YES		0	
deposit_price	varchar(55)	YES		0	
unpaid_amount	varchar(55)	YES		0	
```
행 수: 562

### user_wholesale_contract
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
user_id	int(11)	NO		NULL	
month_price	int(10) unsigned	NO		0	
goods_create_num	smallint(3) unsigned	NO		0	
contract_date_start	date	NO		0000-00-00	
contract_date_extend	date	NO		0000-00-00	
contract_date_changed	date	NO		0000-00-00	
first_month_benefit_date_start	date	NO		0000-00-00	
first_month_benefit_date_end	date	NO		0000-00-00	
add_goods_price	mediumint(7) unsigned	NO		0	
add_model_price	mediumint(7) unsigned	NO		0	
add_color_price	mediumint(7) unsigned	NO		0	
model_add_price	mediumint(7) unsigned	NO		0	
color_add_price	mediumint(7) unsigned	NO		0	
etc_add_price	mediumint(7) unsigned	NO		0	
total_contract_price	int(10) unsigned	NO		0	
change_content	varchar(100)	YES		NULL	
memo	text	YES		NULL	
created	datetime	NO		0000-00-00 00:00:00	
modified	timestamp	NO		current_timestamp()	on update current_timestamp()
no_apply_check	varchar(55)	YES		NULL	
goods_amount_import	varchar(50)	YES		NULL	
good_id	varchar(50)	YES		NULL	
Start_import_date	varchar(50)	YES		NULL	
End_import_date	varchar(50)	YES		NULL	
contract_status	tinyint(1)	YES		1	
apply_priceChange_date	varchar(50)	YES		NULL	
changer_name	varchar(50)	YES		NULL	
EndDate	date	YES		NULL	
username	varchar(50)	YES		NULL	
code	varchar(50)	YES		NULL	
number2Month	int(11)	YES		NULL	
number1Month	int(11)	YES		NULL	
numberCurrent	int(11)	YES		NULL	
pre_goods_create_num	int(11)	YES		0	
allow_carryover	tinyint(1)	NO		0	
company_add	varchar(255)	YES		NULL	
company_name_dage	varchar(255)	YES		NULL	
company_phone	varchar(255)	YES		NULL	
```
행 수: 80

### user_wholesale_contract_history
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
user_id	int(11)	NO	MUL	NULL	
data	text	YES		NULL	
contract_date_changed	char(7)	NO		0000-00	
created	datetime	NO		0000-00-00 00:00:00	
```
행 수: 8

### users
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
auth_code	varchar(10)	NO	MUL	3	
userid	varchar(50)	NO	UNI	NULL	
username	varchar(50)	NO	MUL	NULL	
nickname	varchar(50)	NO	MUL	NULL	
password	varchar(255)	NO	MUL	NULL	
email	varchar(100)	YES		NULL	
hp	varchar(20)	YES		NULL	
danharooid	varchar(50)	YES	MUL	NULL	
activated	tinyint(1)	NO		0	
banned	tinyint(1)	NO		0	
ban_reason	varchar(255)	YES		NULL	
new_password_key	varchar(50)	YES		NULL	
new_password_requested	datetime	YES		NULL	
new_email	varchar(100)	YES		NULL	
new_email_key	varchar(50)	YES		NULL	
down_level	char(1)	NO	MUL	0	
down_level_requested	datetime	NO		0000-00-00 00:00:00	
enter_store_yn	char(1)	NO	MUL	N	
use_end_day	date	YES	MUL	0000-00-00	
use_end_day_requested	date	NO	MUL	0000-00-00	
use_end_day_price	int(10) unsigned	NO		0	
goods_cnt	varchar(5)	NO		0	
sabangnet_id	varchar(50)	YES		NULL	
brandAll	char(1)	NO		N	
brandEtc	varchar(255)	YES		NULL	
brandEtcSub1	varchar(255)	YES		NULL	
brandEtcSub2	varchar(255)	YES		NULL	
last_ip	varchar(40)	YES		NULL	
last_login	datetime	NO		0000-00-00 00:00:00	
created	datetime	NO	MUL	0000-00-00 00:00:00	
modified	timestamp	NO		current_timestamp()	on update current_timestamp()
ios_id	varchar(255)	YES		NULL	
android_id	varchar(255)	YES		NULL	
add_user_id	int(11)	YES		NULL	
memo	text	YES		NULL	
push_all_yn	char(1)	NO		Y	
unregister_yn	char(1)	NO		N	
unregister_date	datetime	NO		NULL	
```
행 수: 79460

### users_2024062705
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
auth_code	varchar(10)	NO		3	
userid	varchar(50)	NO	UNI	NULL	
username	varchar(50)	NO	MUL	NULL	
nickname	varchar(50)	NO	MUL	NULL	
password	varchar(255)	NO	MUL	NULL	
email	varchar(100)	YES		NULL	
hp	varchar(20)	YES		NULL	
danharooid	varchar(50)	YES	MUL	NULL	
activated	tinyint(1)	NO		0	
banned	tinyint(1)	NO		0	
ban_reason	varchar(255)	YES		NULL	
new_password_key	varchar(50)	YES		NULL	
new_password_requested	datetime	YES		NULL	
new_email	varchar(100)	YES		NULL	
new_email_key	varchar(50)	YES		NULL	
down_level	char(1)	NO	MUL	0	
down_level_requested	datetime	NO		0000-00-00 00:00:00	
enter_store_yn	char(1)	NO	MUL	N	
use_end_day	date	YES	MUL	0000-00-00	
use_end_day_requested	date	NO	MUL	0000-00-00	
use_end_day_price	int(10) unsigned	NO		0	
goods_cnt	varchar(5)	NO		0	
sabangnet_id	varchar(50)	YES		NULL	
brandAll	char(1)	NO		N	
brandEtc	varchar(255)	YES		NULL	
brandEtcSub1	varchar(255)	YES		NULL	
brandEtcSub2	varchar(255)	YES		NULL	
last_ip	varchar(40)	YES		NULL	
last_login	datetime	NO		0000-00-00 00:00:00	
created	datetime	NO	MUL	0000-00-00 00:00:00	
modified	timestamp	NO		current_timestamp()	on update current_timestamp()
ios_id	varchar(255)	YES		NULL	
android_id	varchar(255)	YES		NULL	
add_user_id	int(11)	YES		NULL	
memo	text	YES		NULL	
push_all_yn	char(1)	NO		Y	
unregister_yn	char(1)	NO		N	
unregister_date	datetime	NO		NULL	
```
행 수: 76564

### users_2109012314
```sql
Field	Type	Null	Key	Default	Extra
id	int(11)	NO	PRI	NULL	auto_increment
auth_code	varchar(10)	NO		3	
userid	varchar(50)	NO	UNI	NULL	
username	varchar(50)	NO	MUL	NULL	
nickname	varchar(50)	NO	MUL	NULL	
password	varchar(255)	NO	MUL	NULL	
email	varchar(100)	NO		NULL	
hp	varchar(13)	NO		NULL	
danharooid	varchar(50)	NO	MUL	NULL	
activated	tinyint(1)	NO		0	
banned	tinyint(1)	NO		0	
ban_reason	varchar(255)	YES		NULL	
new_password_key	varchar(50)	YES		NULL	
new_password_requested	datetime	YES		NULL	
new_email	varchar(100)	YES		NULL	
new_email_key	varchar(50)	YES		NULL	
down_level	char(1)	NO	MUL	0	
down_level_requested	datetime	NO		0000-00-00 00:00:00	
use_end_day	date	NO	MUL	0000-00-00	
use_end_day_requested	date	NO	MUL	0000-00-00	
use_end_day_price	int(10) unsigned	NO		0	
goods_cnt	varchar(4)	NO		0	
sabangnet_id	varchar(50)	NO		NULL	
brandAll	char(1)	NO		N	
brandEtc	varchar(255)	NO		NULL	
last_ip	varchar(40)	NO		NULL	
last_login	datetime	NO		0000-00-00 00:00:00	
created	datetime	NO	MUL	0000-00-00 00:00:00	
modified	timestamp	NO		current_timestamp()	on update current_timestamp()
ios_id	varchar(255)	YES		NULL	
android_id	varchar(255)	YES		NULL	
add_user_id	int(11)	NO		NULL	
memo	text	NO		NULL	
```
행 수: 5983

