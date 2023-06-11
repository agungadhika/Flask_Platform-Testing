db = new Mongo().getDB("dbuser");

db.createCollection('user', { capped: false });


db.user.insert([
    {
        username: "admin",
        password: "supersecretpassword",
    },
    {
        username: "staf",
        password: "inipasswordnyastaf",
    },
    {
        username: "BukuSakti3000",
        password: "testingpassword123"
    }
])
