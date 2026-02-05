create database Zomato_analytics;

use Zomato_analytics;

IF OBJECT_ID('Reviews') IS NOT NULL DROP TABLE Reviews;
IF OBJECT_ID('Referrals') IS NOT NULL DROP TABLE Referrals;
IF OBJECT_ID('UserSessions') IS NOT NULL DROP TABLE UserSessions;
IF OBJECT_ID('CartItems') IS NOT NULL DROP TABLE CartItems;
IF OBJECT_ID('DeliveryTracking') IS NOT NULL DROP TABLE DeliveryTracking;
IF OBJECT_ID('OrderItems') IS NOT NULL DROP TABLE OrderItems;
IF OBJECT_ID('Orders') IS NOT NULL DROP TABLE Orders;
IF OBJECT_ID('Menu') IS NOT NULL DROP TABLE Menu;
IF OBJECT_ID('Restaurants') IS NOT NULL DROP TABLE Restaurants;
IF OBJECT_ID('Users') IS NOT NULL DROP TABLE Users;
IF OBJECT_ID('Cities') IS NOT NULL DROP TABLE Cities;
IF OBJECT_ID('AcquisitionChannels') IS NOT NULL DROP TABLE AcquisitionChannels;

CREATE TABLE Cities (
    CityID INT IDENTITY(1,1) PRIMARY KEY,
    CityName VARCHAR(100) NOT NULL,
    State VARCHAR(100) NOT NULL,
    CreatedAt DATETIME2 DEFAULT SYSDATETIME()
);

CREATE TABLE AcquisitionChannels (
    ChannelID INT IDENTITY(1,1) PRIMARY KEY,
    ChannelName VARCHAR(100) NOT NULL UNIQUE,
    Description VARCHAR(MAX),
    CreatedAt DATETIME2 DEFAULT SYSDATETIME()
);

CREATE TABLE Users (
    UserID INT IDENTITY(1,1) PRIMARY KEY,
    Username VARCHAR(255) NOT NULL,
    Email VARCHAR(255) NOT NULL UNIQUE,
    PasswordHash VARCHAR(255) NOT NULL,
    Phone VARCHAR(15),
    Address VARCHAR(MAX),
    CityID INT NOT NULL,
    SignUpDate DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    AcquisitionChannelID INT NOT NULL,
    ReferredBy INT,
    LastLoginDate DATETIME2,
    IsActive BIT DEFAULT 1,
    Preferences VARCHAR(MAX),
    CreatedAt DATETIME2 DEFAULT SYSDATETIME(),

    CONSTRAINT FK_Users_City FOREIGN KEY (CityID) REFERENCES Cities(CityID),
    CONSTRAINT FK_Users_Channel FOREIGN KEY (AcquisitionChannelID) REFERENCES AcquisitionChannels(ChannelID),
    CONSTRAINT FK_Users_Referral FOREIGN KEY (ReferredBy) REFERENCES Users(UserID),
    CONSTRAINT CHK_SelfReferral CHECK (UserID <> ReferredBy)
);

CREATE TABLE Restaurants (
    RestaurantID INT IDENTITY(1,1) PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    Address VARCHAR(MAX) NOT NULL,
    CityID INT NOT NULL,
    Cuisine VARCHAR(255),
    Rating DECIMAL(3,2) CHECK (Rating BETWEEN 0 AND 5),
    OperatingHours VARCHAR(255),
    ContactNumber VARCHAR(15),
    IsActive BIT DEFAULT 1,
    OpeningDate DATE,
    CreatedAt DATETIME2 DEFAULT SYSDATETIME(),

    CONSTRAINT FK_Restaurants_City FOREIGN KEY (CityID) REFERENCES Cities(CityID)
);


CREATE TABLE Menu (
    MenuID INT IDENTITY(1,1) PRIMARY KEY,
    RestaurantID INT NOT NULL,
    ItemName VARCHAR(255) NOT NULL,
    Description VARCHAR(MAX),
    Price DECIMAL(10,2) CHECK (Price > 0),
    Category VARCHAR(100),
    CuisineType VARCHAR(100),
    IsVegetarian BIT DEFAULT 0,
    IsAvailable BIT DEFAULT 1,
    CreatedAt DATETIME2 DEFAULT SYSDATETIME(),

    CONSTRAINT FK_Menu_Restaurant FOREIGN KEY (RestaurantID) REFERENCES Restaurants(RestaurantID)
);

CREATE TABLE Orders (
    OrderID INT IDENTITY(1,1) PRIMARY KEY,
    UserID INT NOT NULL,
    RestaurantID INT NOT NULL,
    OrderTime DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    OrderDate DATE NOT NULL,
    OrderDay VARCHAR(10),
    OrderHour INT CHECK (OrderHour BETWEEN 0 AND 23),
    TotalAmount DECIMAL(10,2) CHECK (TotalAmount >= 0),
    DeliveryFee DECIMAL(10,2) DEFAULT 0,
    DiscountAmount DECIMAL(10,2) DEFAULT 0,
    FinalAmount DECIMAL(10,2) CHECK (FinalAmount >= 0),
    OrderStatus VARCHAR(50) NOT NULL,
    DeliveryAddress VARCHAR(MAX),
    PaymentMethod VARCHAR(50),
    CreatedAt DATETIME2 DEFAULT SYSDATETIME(),

    CONSTRAINT FK_Orders_User FOREIGN KEY (UserID) REFERENCES Users(UserID),
    CONSTRAINT FK_Orders_Restaurant FOREIGN KEY (RestaurantID) REFERENCES Restaurants(RestaurantID),
    CONSTRAINT CHK_OrderDate CHECK (OrderDate = CAST(OrderTime AS DATE)),
    CONSTRAINT CHK_FinalAmount CHECK (FinalAmount = TotalAmount + DeliveryFee - DiscountAmount)
);


CREATE TABLE OrderItems (
    OrderItemID INT IDENTITY(1,1) PRIMARY KEY,
    OrderID INT NOT NULL,
    MenuID INT NOT NULL,
    Quantity INT CHECK (Quantity > 0),
    ItemPrice DECIMAL(10,2) CHECK (ItemPrice > 0),
    Subtotal DECIMAL(10,2),

    CreatedAt DATETIME2 DEFAULT SYSDATETIME(),

    CONSTRAINT FK_OrderItems_Order FOREIGN KEY (OrderID) REFERENCES Orders(OrderID) ON DELETE CASCADE,
    CONSTRAINT FK_OrderItems_Menu FOREIGN KEY (MenuID) REFERENCES Menu(MenuID),
    CONSTRAINT CHK_Subtotal CHECK (Subtotal = ItemPrice * Quantity)
);


CREATE TABLE DeliveryTracking (
    DeliveryID INT IDENTITY(1,1) PRIMARY KEY,
    OrderID INT UNIQUE NOT NULL,
    DispatchTime DATETIME2,
    EstimatedDeliveryTime DATETIME2,
    ActualDeliveryTime DATETIME2,
    ActualDeliveryMinutes INT,
    DeliveryPartnerID INT,
    DeliveryStatus VARCHAR(50),
    CreatedAt DATETIME2 DEFAULT SYSDATETIME(),

    CONSTRAINT FK_Delivery_Order FOREIGN KEY (OrderID) REFERENCES Orders(OrderID) ON DELETE CASCADE,
    CONSTRAINT CHK_DeliveryTime CHECK (
        ActualDeliveryTime IS NULL OR ActualDeliveryTime >= DispatchTime
    )
);


CREATE TABLE CartItems (
    CartID INT IDENTITY(1,1) PRIMARY KEY,
    UserID INT NOT NULL,
    RestaurantID INT NOT NULL,
    MenuID INT NOT NULL,
    Quantity INT CHECK (Quantity > 0),
    AddedAt DATETIME2 DEFAULT SYSDATETIME(),
    IsOrdered BIT DEFAULT 0,
    OrderID INT NULL,
    CreatedAt DATETIME2 DEFAULT SYSDATETIME(),

    CONSTRAINT FK_Cart_User FOREIGN KEY (UserID) REFERENCES Users(UserID),
    CONSTRAINT FK_Cart_Restaurant FOREIGN KEY (RestaurantID) REFERENCES Restaurants(RestaurantID),
    CONSTRAINT FK_Cart_Menu FOREIGN KEY (MenuID) REFERENCES Menu(MenuID),
    CONSTRAINT FK_Cart_Order FOREIGN KEY (OrderID) REFERENCES Orders(OrderID)
);

CREATE TABLE UserSessions (
    SessionID INT IDENTITY(1,1) PRIMARY KEY,
    UserID INT NOT NULL,
    SessionStart DATETIME2 NOT NULL,
    SessionEnd DATETIME2,
    OrderPlaced BIT DEFAULT 0,
    OrderID INT,
    PagesViewed INT DEFAULT 0,
    DeviceType VARCHAR(50),
    CreatedAt DATETIME2 DEFAULT SYSDATETIME(),

    CONSTRAINT FK_Session_User FOREIGN KEY (UserID) REFERENCES Users(UserID),
    CONSTRAINT FK_Session_Order FOREIGN KEY (OrderID) REFERENCES Orders(OrderID),
    CONSTRAINT CHK_SessionTime CHECK (
        SessionEnd IS NULL OR SessionEnd >= SessionStart
    )
);


CREATE TABLE Referrals (
    ReferralID INT IDENTITY(1,1) PRIMARY KEY,
    ReferrerUserID INT NOT NULL,
    ReferredUserID INT NOT NULL UNIQUE,
    ReferralDate DATETIME2 DEFAULT SYSDATETIME(),
    RewardAmount DECIMAL(10,2) DEFAULT 0,
    RewardStatus VARCHAR(50),
    CreatedAt DATETIME2 DEFAULT SYSDATETIME(),

    CONSTRAINT FK_Referral_Referrer FOREIGN KEY (ReferrerUserID) REFERENCES Users(UserID),
    CONSTRAINT FK_Referral_Referred FOREIGN KEY (ReferredUserID) REFERENCES Users(UserID)
);