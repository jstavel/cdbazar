show tables;

describe auth_user;

select * from auth_user limit 10;
select * from workflow_instance limit 10;

select count(*) from workflow_instance;

select count(*) from workflow_state;

select * from workflow_state limit 10;
select * from workflow_workflowmembership limit 10;
select * from workflow_instancemembership limit 10;
select * from workflow_instance limit 10;

select count(*) from store_article;

select count(*) from store_item;

describe store_item;

select * from store_item order by lastUpdated desc limit 10;

show tables;

describe store_articleitemstate;


describe workflow_instance;
describe workflow_workflow;
describe store_item;

select * from workflow_workflow;

select * from store_article limit 10;

describe store_article;

describe store_picture;

select * from store_item limit 10;

select * from store_picture limit 1;