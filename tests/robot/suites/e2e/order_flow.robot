*** Settings ***
Documentation     E2E workflow for placing an order against seeded demo data.
Library           DataDriver    file=${CURDIR}/../../data/customer_order_flow.csv    encoding=utf-8
Resource          ../../resources/api.resource
Suite Setup       Prepare API Session
Suite Teardown    Close API Session
Test Template     Customer Order Workflow

*** Test Cases ***
Customer order workflow from CSV - ${customer_email} - ${product_name}

*** Keywords ***
Customer Order Workflow
    [Arguments]    ${customer_email}    ${category_name}    ${category_description}    ${product_name}    ${product_description}    ${product_price}    ${product_stock}    ${order_quantity}    ${order_date}    ${expected_order_status}

    ${customer}=    Find Item By Field    /customers    email    ${customer_email}
    ${customer_id}=    Get From Dictionary    ${customer}    id

    ${category}    ${category_id}=    Create Category    ${category_name}    ${category_description}
    ${product_summary}=    Create Product    ${product_name}    ${product_description}    ${product_price}    ${product_stock}    ${category_id}
    ${product_before}=    Get From Dictionary    ${product_summary}    body
    ${product_id}=    Get From Dictionary    ${product_summary}    id
    ${product_price}=    Get From Dictionary    ${product_summary}    price
    ${product_stock_before}=    Get From Dictionary    ${product_summary}    stock

    ${order}    ${order_id}=    Create Order    ${customer_id}    ${order_date}    ${expected_order_status}
    ${order_item}    ${order_item_id}=    Create Order Item    ${order_id}    ${product_id}    ${order_quantity}    ${product_price}

    ${order_after}=    Get Resource By Id    /orders    ${order_id}
    ${product_after}=    Get Resource By Id    /products    ${product_id}

    ${order_total}=    Get From Dictionary    ${order_after}    total_amount
    ${order_status}=    Get From Dictionary    ${order_after}    status
    ${product_stock_after}=    Get From Dictionary    ${product_after}    stock_quantity

    ${expected_total}=    Evaluate    int(${product_price}) * int(${order_quantity})
    Assert Equal Integer Fields    ${order_after}    total_amount    ${expected_total}
    Should Be Equal    ${order_status}    ${expected_order_status}
    Assert Integer Difference    ${product_stock_before}    ${product_stock_after}    ${order_quantity}

    Delete Resource    /order-items    ${order_item_id}
    Delete Resource    /orders    ${order_id}
    Delete Resource    /products    ${product_id}
    Delete Resource    /categories    ${category_id}
