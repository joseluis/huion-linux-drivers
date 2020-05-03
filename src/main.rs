use rusb::Error;

const HUION_VENDOR_ID:  u16 = 0x256c;
const HUION_PRODUCT_ID: u16 = 0x006e;

fn main() {


    if let Ok((num,addr)) = search_tablet() {
        println!("Tablet found at bus {}, address: {}", num, addr)
    } else {
        println!("Tablet not found")
    }

}

///
fn search_tablet() -> Result<(u8,u8), Error>{
    for device in rusb::devices().unwrap().iter() {
        let device_desc = device.device_descriptor().unwrap();
        if device_desc.vendor_id() == HUION_VENDOR_ID && device_desc.product_id() == HUION_PRODUCT_ID {
            return Ok((device.bus_number(), device.address()));
        }
    }
    Err(Error::NotFound)
}

