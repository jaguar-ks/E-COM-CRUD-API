*** Settings ***
Library           Collections
# Library           DateTime
Library           RequestsLibrary

*** Variables ***
${BASE_URL}       http://127.0.0.1:8000
${API_ALIAS}      ecom_api

*** Keywords ***
Prepare API Session
    Create Session    ${API_ALIAS}    ${BASE_URL}
    API Should Be Healthy

Close API Session
    Delete All Sessions

API Should Be Healthy
    ${response}=    GET On Session    ${API_ALIAS}    /
    Should Be Equal As Integers    ${response.status_code}    200
    ${body}=    Evaluate    $response.json()
    Dictionary Should Contain Item    ${body}    message    Hello There!!

Get Collection By Endpoint
    [Arguments]    ${endpoint}
    ${response}=    GET On Session    ${API_ALIAS}    ${endpoint}
    Should Be Equal As Integers    ${response.status_code}    200
    ${items}=    Evaluate    $response.json()
    RETURN    ${items}

Find Item By Field
    [Arguments]    ${endpoint}    ${field_name}    ${field_value}
    @{items}=    Get Collection By Endpoint    ${endpoint}
    FOR    ${item}    IN    @{items}
        ${candidate}=    Get From Dictionary    ${item}    ${field_name}
        IF    '${candidate}' == '${field_value}'
            RETURN    ${item}
        END
    END
    Fail    Item with ${field_name}=${field_value} was not found in ${endpoint}

Get Resource By Id
    [Arguments]    ${endpoint}    ${resource_id}
    ${response}=    GET On Session    ${API_ALIAS}    ${endpoint}/${resource_id}
    Should Be Equal As Integers    ${response.status_code}    200
    ${body}=    Evaluate    $response.json()
    RETURN    ${body}

Create Resource
    [Arguments]    ${endpoint}    &{payload}
    ${response}=    POST On Session    ${API_ALIAS}    ${endpoint}    json=${payload}
    Should Be Equal As Integers    ${response.status_code}    201
    ${body}=    Evaluate    $response.json()
    RETURN    ${body}

Create Resource Expecting Conflict
    [Arguments]    ${endpoint}    &{payload}
    ${response}=    POST On Session    ${API_ALIAS}    ${endpoint}    json=${payload}    expected_status=any
    Should Be Equal As Integers    ${response.status_code}    409

Delete Resource
    [Arguments]    ${endpoint}    ${resource_id}
    ${response}=    DELETE On Session    ${API_ALIAS}    ${endpoint}/${resource_id}    expected_status=any
    ${status}=    Set Variable    ${response.status_code}
    IF    ${status} == 204
        Return From Keyword
    ELSE IF    ${status} == 409
        Log    Resource ${endpoint}/${resource_id} could not be deleted (409 Conflict)    WARN
        Return From Keyword
    ELSE
        Fail    Unexpected delete status ${status} for ${endpoint}/${resource_id}
    END

Delete Resource Expecting Conflict
    [Arguments]    ${endpoint}    ${resource_id}
    ${response}=    DELETE On Session    ${API_ALIAS}    ${endpoint}/${resource_id}    expected_status=any
    Should Be Equal As Integers    ${response.status_code}    409

Assert Integer Difference
    [Arguments]    ${before}    ${after}    ${delta}
    ${expected}=    Evaluate    int(${before}) - int(${delta})
    Should Be Equal As Integers    ${after}    ${expected}

Assert Equal Integer Fields
    [Arguments]    ${body}    ${field_name}    ${expected_value}
    ${actual}=    Get From Dictionary    ${body}    ${field_name}
    Should Be Equal As Integers    ${actual}    ${expected_value}


Create Category
    [Arguments]    ${name}    ${description}
    &{payload}=    Create Dictionary    name=${name}    description=${description}
    ${response}=    POST On Session    ${API_ALIAS}    /categories    json=${payload}    expected_status=any
    ${status}=    Set Variable    ${response.status_code}
    IF    ${status} == 201
        ${body}=    Evaluate    $response.json()
        ${category_id}=    Get From Dictionary    ${body}    id
        RETURN    ${body}    ${category_id}
    ELSE IF    ${status} == 409
        ${existing}=    Find Item By Field    /categories    name    ${name}
        ${category_id}=    Get From Dictionary    ${existing}    id
        RETURN    ${existing}    ${category_id}
    ELSE
        Fail    Unexpected status ${status} when creating category
    END

Create Customer
    [Arguments]    ${first_name}    ${last_name}    ${email}    ${phone}
    &{payload}=    Create Dictionary    first_name=${first_name}    last_name=${last_name}    email=${email}    phone=${phone}
    ${response}=    POST On Session    ${API_ALIAS}    /customers    json=${payload}    expected_status=any
    ${status}=    Set Variable    ${response.status_code}
    IF    ${status} == 201
        ${body}=    Evaluate    $response.json()
        ${customer_id}=    Get From Dictionary    ${body}    id
        RETURN    ${body}    ${customer_id}
    ELSE IF    ${status} == 409
        ${existing}=    Find Item By Field    /customers    email    ${email}
        ${customer_id}=    Get From Dictionary    ${existing}    id
        RETURN    ${existing}    ${customer_id}
    ELSE
        Fail    Unexpected status ${status} when creating customer
    END

Create Product
    [Arguments]    ${name}    ${description}    ${price}    ${stock}    ${category_id}
    &{payload}=    Create Dictionary    name=${name}    description=${description}    price=${price}    stock_quantity=${stock}    category_id=${category_id}
    ${product}=    Create Resource    /products    &{payload}
    ${product_id}=    Get From Dictionary    ${product}    id
    ${product_price}=    Get From Dictionary    ${product}    price
    ${product_stock}=    Get From Dictionary    ${product}    stock_quantity
    &{summary}=    Create Dictionary    body=${product}    id=${product_id}    price=${product_price}    stock=${product_stock}
    RETURN    &{summary}

Create Order
    [Arguments]    ${customer_id}    ${order_date}    ${status}=Pending
    &{payload}=    Create Dictionary    customer_id=${customer_id}    order_date=${order_date}    total_amount=0    status=${status}
    ${order}=    Create Resource    /orders    &{payload}
    ${order_id}=    Get From Dictionary    ${order}    id
    RETURN    ${order}    ${order_id}

Create Order Item
    [Arguments]    ${order_id}    ${product_id}    ${quantity}    ${price}
    &{payload}=    Create Dictionary    order_id=${order_id}    product_id=${product_id}    quantity=${quantity}    price=${price}
    ${order_item}=    Create Resource    /order-items    &{payload}
    ${order_item_id}=    Get From Dictionary    ${order_item}    id
    RETURN    ${order_item}    ${order_item_id}
