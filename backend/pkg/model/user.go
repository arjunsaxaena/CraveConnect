package model

import (
	"errors"
)

type User struct {
	BaseEntity
	IPerson
	Id               string `json:"id" db:"id"`
	PreferenceTags   *[]string `json:"preference_tags" db:"preference_tags"`
	DietaryRestrictions *[]string `json:"dietary_restrictions" db:"dietary_restrictions"`
	DefaultAddressId   *string `json:"default_address_id" db:"default_address_id"`
}

type GetUserFilters struct {
	Id           *string `json:"id" db:"id"`
	Name         *string `json:"name" db:"name"`
	Email        *string `json:"email" db:"email"`
	Phone        *string `json:"phone" db:"phone"`
	AuthProvider *string `json:"auth_provider" db:"auth_provider"`
	IsActive     *bool   `json:"is_active" db:"is_active"`
}

func ValidateUser(user *User) error {
	if user.Name == "" {
		return errors.New("name is required")
	}
	if user.Email == "" && user.Phone == "" {
		return errors.New("either email or phone is required")
	}
	if user.AuthProvider == "" {
		return errors.New("auth provider is required")
	}
	if user.AuthProvider != AuthProviderGoogle && user.AuthProvider != AuthProviderPhone {
		return errors.New("invalid auth provider")
	}
	return nil
}

//////////////////////////////////////////////////////////////////////////////////////////

type UserAddress struct {
	BaseEntity
	Id               string `json:"id" db:"id"`
	UserId           string `json:"user_id" db:"user_id"`
	AddressLine1     string `json:"address_line1" db:"address_line1"`
	AddressLine2     *string `json:"address_line2" db:"address_line2"`
	City             string `json:"city" db:"city"`
	State            string `json:"state" db:"state"`
	PostalCode       string `json:"postal_code" db:"postal_code"`
	Country          string `json:"country" db:"country"`
	AliasName        *string `json:"alias_name" db:"alias_name"`
	GeoPoint         *string `json:"geo_point" db:"geo_point"`
	IsPrimary        bool   `json:"is_primary" db:"is_primary"`
}

type GetUserAddressFilters struct {
	Id           *string `json:"id" db:"id"`
	UserId       *string `json:"user_id" db:"user_id"`
	PostalCode   *string `json:"postal_code" db:"postal_code"`
	IsPrimary    *bool   `json:"is_primary" db:"is_primary"`
	IsActive     *bool   `json:"is_active" db:"is_active"`
}

func ValidateUserAddress(userAddress *UserAddress) error {
	if userAddress.UserId == "" {
		return errors.New("user id is required")
	}
	if userAddress.AddressLine1 == "" {
		return errors.New("address line 1 is required")
	}
	if userAddress.City == "" {
		return errors.New("city is required")
	}
	if userAddress.State == "" {
		return errors.New("state is required")
	}
	if userAddress.PostalCode == "" {
		return errors.New("postal code is required")
	}
	if userAddress.Country == "" {
		return errors.New("country is required")
	}
	return nil
}

