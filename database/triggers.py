# define some triggers
triggers = [
    # to update qty in cart based on number of detail_carts
    """
    CREATE TRIGGER update_cart_qty_on_insert_detail_cart_trigger 
    AFTER INSERT
    ON detail_cart
    FOR EACH ROW 
    BEGIN
        DECLARE cart_qty_insert INTEGER;
        SELECT COUNT(*) INTO cart_qty_insert FROM detail_cart WHERE cart_id = NEW.cart_id;
        UPDATE cart SET qty = cart_qty_insert WHERE id = NEW.cart_id;
    END
    """,
    # to update qty in cart based on number of detail_carts
    """
    CREATE TRIGGER update_cart_qty_on_delete_detail_cart_trigger 
    AFTER DELETE
    ON detail_cart
    FOR EACH ROW 
    BEGIN  
        DECLARE cart_qty_delete INTEGER;
        SELECT COUNT(*) INTO cart_qty_delete FROM detail_cart WHERE cart_id = OLD.cart_id;
        UPDATE cart SET qty = cart_qty_delete WHERE id = OLD.cart_id;
    END
    """,
    # to update is_available in detail_cart based on qty in product
    """
    CREATE TRIGGER update_detail_cart_is_available_on_update_product_trigger 
    AFTER UPDATE
    ON product
    FOR EACH ROW 
    BEGIN
        UPDATE detail_cart
        SET is_available = CASE
            WHEN (SELECT available_qty FROM product WHERE id = NEW.id) > 0 THEN 1
            ELSE 0
            END
        WHERE product_id = NEW.id;
    END;
    """,
    # to update qty in detail_cart based on product qty
    """
    CREATE TRIGGER update_detail_cart_qty_on_update_product_trigger
    AFTER UPDATE 
    ON product
    FOR EACH ROW
    BEGIN
        IF NEW.available_qty != OLD.available_qty THEN
            UPDATE detail_cart cd
            SET cd.qty = CASE
                            WHEN cd.qty > NEW.available_qty THEN NEW.available_qty
                            ELSE cd.qty
                        END
            WHERE cd.product_id = NEW.id;
        END IF;
    END;
    """,
    # to update ordered_qty in product everytime insertion on detail_order
    """
    CREATE TRIGGER update_product_ordered_qty_on_insert_detail_order_trigger
    AFTER INSERT 
    ON detail_order
    FOR EACH ROW
    BEGIN
        UPDATE product p
        SET p.ordered_qty = (
            SELECT SUM(qty) 
            FROM detail_order 
            WHERE order_id IN (
                SELECT id 
                FROM `order` 
                WHERE status IN ('active', 'sent')
            ) AND product_id = NEW.product_id
        )
        WHERE p.id = NEW.product_id;
    END;
    """,
    # to update qty in order based on insertion on detail_order
    """
    CREATE TRIGGER update_order_qty_on_insert_detail_order_trigger
    AFTER INSERT 
    ON detail_order
    FOR EACH ROW
    BEGIN
        UPDATE `order` o
        SET o.qty = (
            SELECT COUNT(*)
            FROM detail_order
            WHERE order_id = o.id
        )
        WHERE o.id = NEW.order_id;
    END;
    """,
    # to update ordered_qty in product everytime updation on order
    """
    CREATE TRIGGER update_product_ordered_qty_on_update_order_trigger
    AFTER UPDATE 
    ON `order`
    FOR EACH ROW
    BEGIN
        UPDATE product p
        SET p.ordered_qty = (
            SELECT SUM(qty)
            FROM detail_order
            WHERE order_id IN (
                SELECT id 
                FROM `order` 
                WHERE status IN ('active', 'sent')
            ) AND product_id = p.id
        )
        WHERE p.id IN (SELECT product_id from detail_order WHERE order_id=NEW.id);
    END;
    """,
    # to update total_qty in product everytime updation on product
    """
    CREATE TRIGGER update_product_total_qty_on_update_product_trigger
    BEFORE UPDATE 
    ON product
    FOR EACH ROW
    SET NEW.total_qty = COALESCE(NEW.ordered_qty, 0) + COALESCE(NEW.available_qty, 0);
    """,
    # to update available_qty in warehouse based on product available_qty
    """
    CREATE TRIGGER update_warehouse_available_qty_on_update_product_trigger
    AFTER UPDATE 
    ON product
    FOR EACH ROW
    BEGIN
        UPDATE warehouse w
        SET w.available_qty = (SELECT SUM(available_qty) FROM `product`);
    END;
    """,
    # to update ordered_qty in warehouse based on product ordered_qty
    """
    CREATE TRIGGER update_warehouse_ordered_qty_on_update_product_trigger
    AFTER UPDATE 
    ON product
    FOR EACH ROW
    BEGIN
        UPDATE warehouse w
        SET w.ordered_qty = (SELECT SUM(ordered_qty) FROM `product`);
    END;
    """,
    # to update total_qty in warehouse based on product total_qty
    """
    CREATE TRIGGER update_warehouse_total_qty_on_update_product_trigger
    AFTER UPDATE 
    ON product
    FOR EACH ROW
    BEGIN
        UPDATE warehouse w
        SET w.total_qty = (SELECT SUM(total_qty) FROM `product`);
    END;
    """,
]