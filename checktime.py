import json

def load_schedule(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def check_time_slots(schedule):
    valid_time_slots = [
        "08:30-09:20", "09:30-10:20", "10:30-11:20", "11:30-12:20",
        "13:30-14:20", "14:30-15:20", "15:30-16:20",
        "16:30-17:20", "17:30-18:20", "18:30-19:20", "19:30-20:20",
        "20:30-21:20"
    ]
    
    invalid_time_slots = []

    for day, classes in schedule.items():
        for class_name, details in classes.items():
            for cls in details['dersler']:
                for slot in cls['saatler']:
                    if slot not in valid_time_slots:
                        invalid_time_slots.append((day, class_name, slot))

    return invalid_time_slots

def main():
    # JSON dosyasını yükleyin
    schedule = load_schedule('forQR.json')

    # Geçersiz saat aralıklarını kontrol edin
    invalid_time_slots = check_time_slots(schedule)

    if invalid_time_slots:
        print("Geçersiz saat aralıkları bulundu:")
        for day, class_name, slot in invalid_time_slots:
            print(f"Gün: {day}, Derslik: {class_name}, Saat: {slot}")
    else:
        print("Tüm saat aralıkları geçerli.")

if __name__ == "__main__":
    main()
